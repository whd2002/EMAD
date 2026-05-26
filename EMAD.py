import math
import heapq
import os
import pandas as pd

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional


# ============================================================
# 1. 基础数据结构
# ============================================================

@dataclass
class User:
    """
    能源市场中的用户。

    对应论文中的 Energy User。

    每个用户包含：
    1. uid：用户编号
    2. dex_id：用户所属的本地 DEX
    3. e_token：用户持有的能源代币数量
    4. m_token：用户持有的货币代币数量
    """
    uid: str
    dex_id: str
    e_token: float
    m_token: float


@dataclass
class DEXPool:
    """
    AMM-based DEX 流动性池。

    对应论文中的 AMM liquidity pool。

    池子中有两种资产：
    1. E-Token reserve：能源储备
    2. M-Token reserve：货币储备

    AMM 使用 Uniswap V2 的恒定乘积公式：

        E_LP * M_LP = K
    """
    dex_id: str
    e_reserve: float
    m_reserve: float

    @property
    def k(self) -> float:
        """
        AMM 恒定乘积 K。

        论文公式：
            E_LP^j * M_LP^j = K_j
        """
        return self.e_reserve * self.m_reserve

    def price(self) -> float:
        """
        当前池子的即时能源价格。

        论文公式：
            alpha_LP = M_LP / E_LP
        """
        if self.e_reserve <= 0:
            return math.inf
        return self.m_reserve / self.e_reserve

    def buy_energy_cost(self, e_out: float) -> float:
        """
        计算从 AMM 池子中买出 e_out 数量的 E-Token
        需要支付多少 M-Token。

        论文公式：
            M_i = K / (E_LP - E_i) - M_LP

        参数：
            e_out：买家希望从池中取出的能源数量

        返回：
            所需支付的 M-Token 数量
        """
        if e_out <= 0:
            return 0.0

        if e_out >= self.e_reserve:
            return math.inf

        k_before = self.k

        new_e_reserve = self.e_reserve - e_out
        new_m_reserve = k_before / new_e_reserve

        m_required = new_m_reserve - self.m_reserve

        return m_required

    def execute_buy(self, e_out: float, m_in: float):
        """
        执行 AMM 交易后，更新池子状态。

        买家从池子拿走 e_out 个 E-Token，
        同时向池子支付 m_in 个 M-Token。

        更新：
            E_LP = E_LP - e_out
            M_LP = M_LP + m_in
        """
        if e_out <= 0:
            raise ValueError("e_out must be positive.")

        if e_out >= self.e_reserve:
            raise ValueError("Not enough E-Token reserve in pool.")

        self.e_reserve -= e_out
        self.m_reserve += m_in


@dataclass
class BuyOrder:
    """
    买单。

    对应论文中的：
        B_{i,u} = {E_buy, L_u, j <- u}

    简化后保留：
    1. buyer_id：买家编号
    2. e_buy：买家希望最终收到的能源数量
    """
    buyer_id: str
    e_buy: float


@dataclass
class SellOrder:
    """
    卖单。

    对应论文中的：
        S_{i,u} = {E_sell, L_u, j <- u}

    简化后保留：
    1. seller_id：卖家编号
    2. e_sell_max：卖家最大可出售能源数量
    """
    seller_id: str
    e_sell_max: float


@dataclass
class Edge:
    """
    电网中的一条有向输电线路。

    参数：
    1. to_node：线路终点
    2. loss_rate：线路损耗率 l_{m,n}
    3. capacity：线路容量限制 P_max
    """
    to_node: str
    loss_rate: float
    capacity: float


@dataclass
class Network:
    """
    能源网络。

    对应论文中的：
        G = (V, L, W)

    这里使用图结构表示：
        graph[from_node] = [Edge(...), Edge(...)]
    """
    graph: Dict[str, List[Edge]] = field(default_factory=dict)

    def add_edge(
        self,
        from_node: str,
        to_node: str,
        loss_rate: float,
        capacity: float
    ):
        """
        添加一条有向输电边。

        from_node -> to_node
        """
        self.graph.setdefault(from_node, []).append(
            Edge(
                to_node=to_node,
                loss_rate=float(loss_rate),
                capacity=float(capacity)
            )
        )

    def best_retention_path(
        self,
        source: str,
        target: str,
        required_energy: float
    ) -> Optional[Tuple[List[str], float]]:
        """
        寻找从 source 到 target 的最优输电路径。

        论文中的路径保留率：
            rho_P = product(1 - l_{m,n})

        目标：
            选择能量保留率 rho_P 最大的路径。

        因为 rho_P 是乘法形式，不方便直接用最短路算法，
        所以做如下转换：

            maximize product(rho)
        等价于：
            minimize -log(product(rho))
        也就是：
            minimize sum(-log(rho))

        因此可以用 Dijkstra 思想求解。

        参数：
            source：起点 DEX
            target：终点 DEX
            required_energy：买家希望收到的能源数量

        返回：
            path：最优路径节点序列
            retention：路径总保留率 rho_P
        """
        priority_queue = [
            (0.0, source, [source], 1.0)
        ]

        best_cost = {}

        while priority_queue:
            cost, node, path, retention = heapq.heappop(priority_queue)

            if node == target:
                return path, retention

            if node in best_cost and cost >= best_cost[node]:
                continue

            best_cost[node] = cost

            for edge in self.graph.get(node, []):
                if edge.capacity < required_energy:
                    continue

                rho = 1.0 - edge.loss_rate

                if rho <= 0:
                    continue

                new_retention = retention * rho
                new_cost = cost - math.log(rho)

                heapq.heappush(
                    priority_queue,
                    (
                        new_cost,
                        edge.to_node,
                        path + [edge.to_node],
                        new_retention
                    )
                )

        return None


# ============================================================
# 2. CSV 数据加载函数
# ============================================================

def load_users(path: str) -> Dict[str, User]:
    """
    从 CSV 文件读取用户数据。

    CSV 格式：

        uid,dex_id,e_token,m_token
        buyer_1,DEX_A,0,100000
        seller_1,DEX_B,1000,0
        seller_2,DEX_C,800,0
    """
    df = pd.read_csv(path)

    required_cols = {"uid", "dex_id", "e_token", "m_token"}

    if not required_cols.issubset(df.columns):
        raise ValueError(f"users.csv 缺少字段: {required_cols - set(df.columns)}")

    users = {}

    for _, row in df.iterrows():
        uid = str(row["uid"])

        users[uid] = User(
            uid=uid,
            dex_id=str(row["dex_id"]),
            e_token=float(row["e_token"]),
            m_token=float(row["m_token"])
        )

    return users


def load_pools(path: str) -> Dict[str, DEXPool]:
    """
    从 CSV 文件读取 DEX 流动池数据。

    CSV 格式：

        dex_id,e_reserve,m_reserve
        DEX_A,10000,1500000
        DEX_B,10000,1500000
        DEX_C,10000,1500000
    """
    df = pd.read_csv(path)

    required_cols = {"dex_id", "e_reserve", "m_reserve"}

    if not required_cols.issubset(df.columns):
        raise ValueError(f"pools.csv 缺少字段: {required_cols - set(df.columns)}")

    pools = {}

    for _, row in df.iterrows():
        dex_id = str(row["dex_id"])

        pools[dex_id] = DEXPool(
            dex_id=dex_id,
            e_reserve=float(row["e_reserve"]),
            m_reserve=float(row["m_reserve"])
        )

    return pools


def load_network(path: str) -> Network:
    """
    从 CSV 文件读取电网线路数据。

    CSV 格式：

        from,to,loss_rate,capacity
        DEX_B,DEX_A,0.03,500
        DEX_C,DEX_A,0.05,500
        DEX_B,DEX_C,0.02,300
        DEX_C,DEX_B,0.02,300
    """
    df = pd.read_csv(path)

    required_cols = {"from", "to", "loss_rate", "capacity"}

    if not required_cols.issubset(df.columns):
        raise ValueError(f"network.csv 缺少字段: {required_cols - set(df.columns)}")

    network = Network()

    for _, row in df.iterrows():
        network.add_edge(
            from_node=str(row["from"]),
            to_node=str(row["to"]),
            loss_rate=float(row["loss_rate"]),
            capacity=float(row["capacity"])
        )

    return network


def load_buy_orders(path: str) -> List[BuyOrder]:
    """
    从 CSV 文件读取买单。

    CSV 格式：

        buyer_id,e_buy
        buyer_1,100
        buyer_2,80
    """
    df = pd.read_csv(path)

    required_cols = {"buyer_id", "e_buy"}

    if not required_cols.issubset(df.columns):
        raise ValueError(f"buy_orders.csv 缺少字段: {required_cols - set(df.columns)}")

    buy_orders = []

    for _, row in df.iterrows():
        buy_orders.append(
            BuyOrder(
                buyer_id=str(row["buyer_id"]),
                e_buy=float(row["e_buy"])
            )
        )

    return buy_orders


def load_sell_orders(path: str) -> List[SellOrder]:
    """
    从 CSV 文件读取卖单。

    CSV 格式：

        seller_id,e_sell_max
        seller_1,200
        seller_2,150
    """
    df = pd.read_csv(path)

    required_cols = {"seller_id", "e_sell_max"}

    if not required_cols.issubset(df.columns):
        raise ValueError(f"sell_orders.csv 缺少字段: {required_cols - set(df.columns)}")

    sell_orders = []

    for _, row in df.iterrows():
        sell_orders.append(
            SellOrder(
                seller_id=str(row["seller_id"]),
                e_sell_max=float(row["e_sell_max"])
            )
        )

    return sell_orders


# ============================================================
# 3. EMAD 市场主算法
# ============================================================

@dataclass
class EMADMarket:
    """
    EMAD 主市场类。

    对应论文整体系统：

    1. 接收买单和卖单
    2. 在多个 DEX 中搜索可行交易
    3. 根据 AMM 计算价格
    4. 根据电网损耗选择路径
    5. 最小化总成本 M_i + F_i
    6. 执行交易并更新账户状态
    """
    users: Dict[str, User]
    pools: Dict[str, DEXPool]
    network: Network

    zero_energy_account: float = 0.0
    fee_rate: float = 0.003

    def select_best_trade(
        self,
        buy_order: BuyOrder,
        sell_orders: List[SellOrder]
    ) -> Optional[dict]:
        """
        选择最优交易方案。

        对应论文 Algorithm 1：Path Selection Algorithm。

        优化目标：
            min { M_i + F_i }

        遍历所有卖家：
            1. 获取卖家所属 DEX
            2. 寻找卖家 DEX 到买家 DEX 的最优路径
            3. 根据路径损耗计算卖家实际需要发出的能源 E_i
            4. 检查卖家能源是否足够
            5. 用 AMM 公式计算买家支付的 M_i
            6. 加上手续费 F_i
            7. 选择总成本最低的方案
        """
        if buy_order.buyer_id not in self.users:
            raise ValueError(f"买家不存在: {buy_order.buyer_id}")

        buyer = self.users[buy_order.buyer_id]
        buyer_dex = buyer.dex_id

        best_trade = {
            "total_cost": math.inf,
            "seller_id": None,
            "seller_dex": None,
            "path": None,
            "retention": None,
            "e_dispatch": None,
            "m_payment": None,
            "fee": None
        }

        for sell_order in sell_orders:
            if sell_order.seller_id not in self.users:
                continue

            seller = self.users[sell_order.seller_id]
            seller_dex = seller.dex_id

            if seller_dex not in self.pools:
                continue

            pool = self.pools[seller_dex]

            path_result = self.network.best_retention_path(
                source=seller_dex,
                target=buyer_dex,
                required_energy=buy_order.e_buy
            )

            if path_result is None:
                continue

            path, rho_p = path_result

            if rho_p <= 0:
                continue

            e_dispatch = buy_order.e_buy / rho_p

            if e_dispatch > sell_order.e_sell_max:
                continue

            if e_dispatch > seller.e_token:
                continue

            if e_dispatch >= pool.e_reserve:
                continue

            m_payment = pool.buy_energy_cost(e_dispatch)

            if not math.isfinite(m_payment):
                continue

            fee = self.fee_rate * m_payment
            total_cost = m_payment + fee

            if buyer.m_token < total_cost:
                continue

            if total_cost < best_trade["total_cost"]:
                best_trade.update({
                    "total_cost": total_cost,
                    "seller_id": seller.uid,
                    "seller_dex": seller_dex,
                    "path": path,
                    "retention": rho_p,
                    "e_dispatch": e_dispatch,
                    "m_payment": m_payment,
                    "fee": fee
                })

        if best_trade["seller_id"] is None:
            return None

        return best_trade

    def execute_trade(
        self,
        buy_order: BuyOrder,
        trade_plan: dict
    ) -> dict:
        """
        执行选出的最优交易。

        对应论文 Algorithm 2：Energy Transaction Algorithm。

        主要更新：

        买家账户：
            M_user = M_user - M_i - F_i
            E_user = E_user + E_buy

        卖家账户：
            M_user = M_user + M_i
            E_user = E_user - E_dispatch

        AMM 池：
            E_LP = E_LP - E_dispatch
            M_LP = M_LP + M_i + F_i

        零账户：
            E_zero = E_zero + E_loss
        """
        buyer = self.users[buy_order.buyer_id]
        seller = self.users[trade_plan["seller_id"]]
        seller_pool = self.pools[trade_plan["seller_dex"]]

        e_buy = buy_order.e_buy
        e_dispatch = trade_plan["e_dispatch"]
        e_loss = e_dispatch - e_buy

        m_payment = trade_plan["m_payment"]
        fee = trade_plan["fee"]
        total_cost = m_payment + fee

        if buyer.m_token < total_cost:
            raise ValueError("买家 M-Token 不足。")

        if seller.e_token < e_dispatch:
            raise ValueError("卖家 E-Token 不足。")

        buyer.m_token -= total_cost
        buyer.e_token += e_buy

        seller.m_token += m_payment
        seller.e_token -= e_dispatch

        seller_pool.execute_buy(
            e_out=e_dispatch,
            m_in=m_payment + fee
        )

        self.zero_energy_account += e_loss

        execution_price = m_payment / e_dispatch if e_dispatch > 0 else math.inf

        return {
            "status": "success",
            "buyer": buyer.uid,
            "seller": seller.uid,
            "buyer_dex": buyer.dex_id,
            "seller_dex": seller.dex_id,
            "path": " -> ".join(trade_plan["path"]),
            "energy_received": e_buy,
            "energy_dispatched": e_dispatch,
            "energy_loss": e_loss,
            "path_retention": trade_plan["retention"],
            "payment": m_payment,
            "fee": fee,
            "total_cost": total_cost,
            "execution_price": execution_price
        }

    def process_buy_order(
        self,
        buy_order: BuyOrder,
        sell_orders: List[SellOrder]
    ) -> dict:
        """
        处理单个买单。

        流程：
            1. 选择最优卖家、DEX、路径
            2. 如果没有可行方案，则交易失败
            3. 如果有可行方案，则执行交易
        """
        trade_plan = self.select_best_trade(
            buy_order=buy_order,
            sell_orders=sell_orders
        )

        if trade_plan is None:
            return {
                "status": "failed",
                "buyer": buy_order.buyer_id,
                "energy_requested": buy_order.e_buy,
                "reason": "No feasible seller, path, liquidity, or balance found"
            }

        return self.execute_trade(
            buy_order=buy_order,
            trade_plan=trade_plan
        )


# ============================================================
# 4. 结果保存函数
# ============================================================

def save_users(users: Dict[str, User], path: str):
    """
    保存交易后的用户账户状态。
    """
    df = pd.DataFrame([
        {
            "uid": user.uid,
            "dex_id": user.dex_id,
            "e_token": user.e_token,
            "m_token": user.m_token
        }
        for user in users.values()
    ])

    df.to_csv(path, index=False)


def save_pools(pools: Dict[str, DEXPool], path: str):
    """
    保存交易后的 DEX 池子状态。
    """
    df = pd.DataFrame([
        {
            "dex_id": pool.dex_id,
            "e_reserve": pool.e_reserve,
            "m_reserve": pool.m_reserve,
            "price": pool.price()
        }
        for pool in pools.values()
    ])

    df.to_csv(path, index=False)


def save_results(results: List[dict], path: str):
    """
    保存每笔交易的执行结果。
    """
    df = pd.DataFrame(results)
    df.to_csv(path, index=False)


# ============================================================
# 5. 主程序入口
# ============================================================

def main():
    """
    主函数。

    默认读取以下文件：

        data/users.csv
        data/pools.csv
        data/network.csv
        data/buy_orders.csv
        data/sell_orders.csv

    输出以下文件：

        output/transaction_results.csv
        output/users_after.csv
        output/pools_after.csv
    """

    user_path = "data/users.csv"
    pool_path = "data/pools.csv"
    network_path = "data/network.csv"
    buy_order_path = "data/buy_orders.csv"
    sell_order_path = "data/sell_orders.csv"

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    users = load_users(user_path)
    pools = load_pools(pool_path)
    network = load_network(network_path)

    buy_orders = load_buy_orders(buy_order_path)
    sell_orders = load_sell_orders(sell_order_path)

    market = EMADMarket(
        users=users,
        pools=pools,
        network=network,
        fee_rate=0.003
    )

    results = []

    for buy_order in buy_orders:
        result = market.process_buy_order(
            buy_order=buy_order,
            sell_orders=sell_orders
        )

        results.append(result)

        print("=" * 80)
        for key, value in result.items():
            print(f"{key}: {value}")

    save_results(
        results,
        os.path.join(output_dir, "transaction_results.csv")
    )

    save_users(
        users,
        os.path.join(output_dir, "users_after.csv")
    )

    save_pools(
        pools,
        os.path.join(output_dir, "pools_after.csv")
    )

    print("\nSimulation finished.")
    print(f"Zero energy account: {market.zero_energy_account}")


if __name__ == "__main__":
    main()
