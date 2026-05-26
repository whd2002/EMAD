import math
import heapq
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional


# =========================
# Data Classes
# =========================

@dataclass
class User:
    uid: str
    dex_id: str
    e_token: float
    m_token: float


@dataclass
class DEXPool:
    dex_id: str
    e_reserve: float
    m_reserve: float

    @property
    def k(self) -> float:
        return self.e_reserve * self.m_reserve

    def price(self) -> float:
        return self.m_reserve / self.e_reserve

    def buy_energy_cost(self, e_out: float) -> float:
        if e_out <= 0:
            return 0.0

        if e_out >= self.e_reserve:
            return math.inf

        new_e = self.e_reserve - e_out
        new_m = self.k / new_e

        return new_m - self.m_reserve

    def execute_buy(self, e_out: float, m_in: float):
        if e_out >= self.e_reserve:
            raise ValueError("Not enough E-Token reserve in pool.")

        self.e_reserve -= e_out
        self.m_reserve += m_in


@dataclass
class BuyOrder:
    buyer_id: str
    e_buy: float


@dataclass
class SellOrder:
    seller_id: str
    e_sell_max: float


@dataclass
class Edge:
    to_node: str
    loss_rate: float
    capacity: float


@dataclass
class Network:
    graph: Dict[str, List[Edge]] = field(default_factory=dict)

    def add_edge(
        self,
        from_node: str,
        to_node: str,
        loss_rate: float,
        capacity: float
    ):
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
        找到能量保留率最高的路径。

        rho_P = product(1 - loss_rate)

        等价转换为最短路径：
        cost = -log(rho)
        """
        pq = [(0.0, source, [source], 1.0)]
        best_cost = {}

        while pq:
            cost, node, path, retention = heapq.heappop(pq)

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
                    pq,
                    (
                        new_cost,
                        edge.to_node,
                        path + [edge.to_node],
                        new_retention
                    )
                )

        return None


# =========================
# CSV Loaders
# =========================

def load_users(path: str) -> Dict[str, User]:
    """
    users.csv 格式：

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
    pools.csv 格式：

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
    network.csv 格式：

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
    buy_orders.csv 格式：

    buyer_id,e_buy
    buyer_1,100
    buyer_2,80
    """
    df = pd.read_csv(path)

    required_cols = {"buyer_id", "e_buy"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"buy_orders.csv 缺少字段: {required_cols - set(df.columns)}")

    return [
        BuyOrder(
            buyer_id=str(row["buyer_id"]),
            e_buy=float(row["e_buy"])
        )
        for _, row in df.iterrows()
    ]


def load_sell_orders(path: str) -> List[SellOrder]:
    """
    sell_orders.csv 格式：

    seller_id,e_sell_max
    seller_1,200
    seller_2,150
    """
    df = pd.read_csv(path)

    required_cols = {"seller_id", "e_sell_max"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"sell_orders.csv 缺少字段: {required_cols - set(df.columns)}")

    return [
        SellOrder(
            seller_id=str(row["seller_id"]),
            e_sell_max=float(row["e_sell_max"])
        )
        for _, row in df.iterrows()
    ]


# =========================
# EMAD Market Main Algorithm
# =========================

@dataclass
class EMADMarket:
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
            raise ValueError("买家 M-Token 不足")

        if seller.e_token < e_dispatch:
            raise ValueError("卖家 E-Token 不足")

        buyer.m_token -= total_cost
        buyer.e_token += e_buy

        seller.m_token += m_payment
        seller.e_token -= e_dispatch

        seller_pool.execute_buy(
            e_out=e_dispatch,
            m_in=m_payment + fee
        )

        self.zero_energy_account += e_loss

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
            "execution_price": m_payment / e_dispatch
        }

    def process_buy_order(
        self,
        buy_order: BuyOrder,
        sell_orders: List[SellOrder]
    ) -> dict:

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


# =========================
# Save Results
# =========================

def save_users(users: Dict[str, User], path: str):
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
    df = pd.DataFrame(results)
    df.to_csv(path, index=False)


# =========================
# Main
# =========================

def main():
    user_path = "data/users.csv"
    pool_path = "data/pools.csv"
    network_path = "data/network.csv"
    buy_order_path = "data/buy_orders.csv"
    sell_order_path = "data/sell_orders.csv"

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

        print("=" * 60)
        for k, v in result.items():
            print(f"{k}: {v}")

    save_results(results, "output/transaction_results.csv")
    save_users(users, "output/users_after.csv")
    save_pools(pools, "output/pools_after.csv")

    print("\nSimulation finished.")
    print("Zero energy account:", market.zero_energy_account)


if __name__ == "__main__":
    main()
