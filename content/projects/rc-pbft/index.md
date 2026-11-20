---
title: "RC-PBFT Extension: Parallel Synchronization for IoT Blockchains"
date: 2025-07-01
description: "Unordered Global Distributed Transaction (UGDT): a synchronization module for the RC-PBFT consensus that orders transactions deterministically inside a time window and verifies the order instead of agreeing on it, evaluated in a Go simulation up to 300,000 TPS."
summary: "Keeping parallel execution consistent in PBFT-based IoT blockchains: the UGDT algorithm orders transactions deterministically inside a time window, verifies the order instead of reaching consensus on it, and repairs late arrivals locally. Simulated in Go up to 300,000 TPS; published in Current Engineering Letters and Reviews."
tags: ["Blockchain", "PBFT", "Consensus", "Distributed Systems", "IoT", "Go", "Simulation"]
categories: ["Projects"]
keywords: ["RC-PBFT", "UGDT", "Unordered Global Distributed Transaction", "parallel PBFT", "blockchain consistency", "deterministic transaction ordering", "parallel transaction execution", "IoT blockchain", "Go simulation"]
role: "Research project; co-author of the resulting paper"
status: "Completed · published"
period: "February to July 2025"
weight: 5
repo: ""
demo: ""
comments: false
---

A research project at INSAT on a consistency problem that appears when blockchains are made fast enough for IoT workloads. It extends **RC-PBFT**, a random-cluster parallel PBFT consensus ([Ben Othmen et al., IEEE ISCC 2023](https://doi.org/10.1109/ISCC58397.2023.10218119); [Abbessi et al., *Cluster Computing*, 2025](https://doi.org/10.1007/s10586-024-04923-4)), with a synchronization module: the **Unordered Global Distributed Transaction** (UGDT) algorithm. The work was published as a letter article in *Current Engineering Letters and Reviews* (see [below](#publication)).

## Background: PBFT and RC-PBFT

IoT blockchains need high throughput and low latency, which rules out the long finality of Proof-of-Work and Proof-of-Stake chains and their sequential smart-contract execution. **PBFT** (Practical Byzantine Fault Tolerance) is the usual alternative: a fixed set of replicas agrees on the order of transactions in three phases (pre-prepare, prepare, commit), and stays correct as long as fewer than one third of them are faulty. Its weakness is communication: every replica talks to every other, so network load grows as O(n²) with n nodes, and the protocol is sensitive to network delays.

**RC-PBFT** (Random Cluster PBFT) reduces that load by splitting validation across **clusters** of nodes chosen cryptographically. Each cluster runs PBFT on its own share of the work, which cuts the message overhead and lets several PBFT instances run **in parallel** across the network.

## The problem: parallelism versus a single execution order

Parallelism makes consistency harder. In a sequential blockchain, the order of transactions is fixed during consensus, before anything is executed, so every node applies the same transactions in the same order and reaches the same state. Once execution is parallel or speculative, nodes can end up with different orders, and two nodes that disagree must **revoke** their execution, reach consensus again, and **re-execute** the aborted transactions. That round trip is expensive, and it is exactly the latency that parallel designs are trying to remove.

The project asked: can nodes reach a single, deterministic execution order without paying for consensus on that order?

## How existing protocols handle synchronization

The paper surveys the main options against IoT constraints: scalability, low latency, deterministic consistency, and tolerance to jitter and intermittent connectivity on resource-constrained devices.

| Approach | How it synchronizes | Limitation for IoT |
|---|---|---|
| **PBFT** | Three-phase, all-to-all agreement among replicas | O(n²) messages; sensitive to network delays such as the ±30 ms common in IoT |
| **IBFT / QBFT** | Leader rotation and reduced message overhead for permissioned networks | Sub-second finality in small clusters, but bottlenecks in dynamic IoT settings |
| **HotStuff** | Leader-driven BFT with O(n) communication per decision and pipelined phases | Assumes partial synchrony, which IoT networks may not provide |
| **DAG protocols** (IOTA Tangle, Hedera Hashgraph) | Transactions attach in parallel to a graph, with gossip and virtual voting | Probabilistic finality and eventual, not deterministic, consistency |
| **Solana Proof-of-History** | Verifiable delay functions timestamp transactions for parallel validation | Needs high-precision clocks and GPU-class hardware, unsuitable for low-power devices |

## The approach: decouple ordering from execution

Instead of agreeing on *what to execute and what its effects are* in one step, UGDT splits the process into an **ordering stage** and an **execution stage**, and replaces consensus on the order with a rule that every honest node computes identically.

### Deterministic ordering inside a time window

Each node collects incoming transactions for a fixed window, **ΔT**. At the end of the window it sorts everything that arrived by a deterministic criterion:

> OrderCriterion = H(block ‖ senderID ‖ salt)

where H is a hash of the block's content, combined with the sender's identity and a random **salt** that all nodes agree on. Transactions from the same client are then ordered by their **nonce**, so a client's own transactions keep their intended sequence.

Because the criterion depends only on the transactions themselves, every node that sees the same set of transactions derives the same order, with no messages exchanged to agree on it. The order is also hard to manipulate: a client sends its transaction to one node of its choice, which forwards it to the network, and even if that node delays or rushes the transaction to give it priority, its position does not depend on when or where it was first received: the order is determined by variables outside any node's control. The window does require clocks to be synchronized across nodes, but only loosely.

The cost is a small amount of finality, since transactions wait for the window to close before they are ordered. That is the trade the design makes to get deterministic consistency without extra network overhead.

### Parallel execution with local dependency handling

Once the order is fixed, each node executes the queue **independently** and the nodes then agree on the **results** in parallel. Contract locks and execution conditions become simpler too: since the order is predetermined, dependencies between transactions can be resolved locally inside each execution thread before the final agreement.

This extends to **lock tables**, which RC-PBFT uses to decide which transactions are truly independent and can be executed or verified in parallel. Instead of one shared lock table that needs constant communication to stay synchronized, each node can keep its own local copy: the order is deterministic, so the dependencies and lock states derived from it are deterministic as well.

### Late transactions are repaired locally

Network conditions mean some transactions will miss their window. Each transaction carries a timestamp, so a node can tell whether it is new or belongs to a window it has already ordered. Every transaction also has a **predetermined position** in its window's order, even if it arrives late or at different times on different nodes, so it can be **inserted retroactively** into the right slot.

Only the late transaction and the transactions that depend on it need to be recalculated. A transaction that calls contract X does not have to be re-executed if only contract Y, which it does not touch, was affected. The same property helps during consensus: a node can tell it is out of sync by looking at the positions and transactions the other nodes are verifying, and insert what it is missing without adding network load.

## The UGDT algorithm

The algorithm wraps the ordering rule in a verification step: nodes exchange the order they computed and execute only when the orders match.

```text
Algorithm Unordered_Global_Distributed_Transaction
  every ΔT:
    1. Collect:   enqueue each transaction received during the window
    2. Sort:      ordered ← Sort(queue, by = OrderCriterion)
    3. Broadcast: send ordered to every node of the distributed ledger
    4. Verify:    if every node reports the same order
                    execute the transactions and empty the queue
                  else
                    go back to step 1
```

The bet is that ordering usually agrees on its own, so a cheap check plus occasional repair costs less than running consensus on every order. The evaluation measures how often that bet fails.

## Simulation

The algorithm was implemented in **Go** and tested in a simulator where network conditions, node count, throughput and the other parameters are configurable. For every run the simulator produces both an **ordered** queue (with UGDT) and an **unordered** one (raw arrival order). Comparing the two shows how much the ordering helps, and checking the ordered queue catches missing data or ordering errors. In the simulation, late transactions are counted into the next window.

| Parameter | Baseline value |
|---|---|
| Transactions | 1,000,000 |
| Clients | 100 |
| Nodes | 10 |
| Arrivals | Poisson process at a configurable TPS |
| Network delay | Gaussian noise, 25 ms mean, +30 ms jitter |
| Window ΔT | 500 ms |

Two metrics are used:

- **Entropy** of the transaction order: for each rank, how uncertain it is which transaction lands there across nodes, averaged over ranks. Lower is better.
- **Misalignment**: the share of transactions whose position differs between nodes because they arrived late. Entropy alone is misleading here, since a single late transaction shifts the whole rest of the block by one position. Misalignment counts the late transactions instead, which are then reinserted with the same correction mechanism used during consensus.

## Results

Throughput was varied from 100 to **300,000 TPS** to test extreme conditions.

{{< figure src="fig1-entropy-vs-tps.png" alt="Line chart of entropy against TPS from 0 to 300,000. The ordered series stays below the unordered series at every point; both rise steeply at low TPS and level off above 50,000 TPS." caption="Entropy of the transaction order for the ordered (UGDT) and unordered series across throughputs (Fig. 1 in the paper)." >}}

The ordered series has **lower entropy than the unordered one in every configuration**, despite the misalignment caused by late transactions.

{{< figure src="fig2-misalignment-vs-tps.png" alt="Line chart of misalignment percentage against TPS. The mismatch rate starts at about 21% at the lowest TPS, drops to about 12% by 10,000 TPS and stays flat up to 300,000 TPS. The mismatch rate divided by the number of ordering operations stays near zero and rises slowly to about 2%." caption="Misalignment between nodes across throughputs, raw and divided by the number of ordering operations (Fig. 2 in the paper)." >}}

Misalignment starts around **21%** at the lowest throughput and drops as TPS rises, levelling off at about 12% in the plot. Better behavior at higher load looks counterintuitive, but the total number of transactions is fixed at one million: higher TPS means fewer ordering rounds, so fewer window boundaries for a transaction to miss. The second curve divides misalignment by the number of ordering operations to make that effect visible.

{{< figure src="fig3-deltat-tuning.png" alt="Line chart of misalignment percentage against DeltaT from 10 to 2,000 ms. Misalignment is near 100% for windows of 50 ms or less, about 66% at 100 ms, 27% at 250 ms, 12% at 500 ms, then falls slowly to about 3% at 1,500 and 2,000 ms." caption="Effect of the window length ΔT on misalignment at 50,000 TPS (Fig. 3 in the paper)." >}}

**ΔT is the main tuning knob.** At 50,000 TPS, longer windows give better alignment, with diminishing returns: in the plot, misalignment is close to 100% for windows of 50 ms or less, about 27% at 250 ms, 12% at 500 ms, and about 3% from 1.5 s on. Since ΔT adds directly to finality, it has to be tuned to the network's actual delays rather than simply made large.

{{< figure src="fig4-misalignment-vs-nodes.png" alt="Line chart of misalignment percentage against node count from 2 to 24. Misalignment is about 6% with 2 nodes, 9% with 4, 12% with 8, and 15% with 16 and 24 nodes." caption="Effect of node count on misalignment at 50,000 TPS and ΔT = 500 ms (Fig. 4 in the paper)." >}}

More nodes amplify the effect of network conditions, but slowly: at 50,000 TPS and ΔT = 500 ms, misalignment follows a **logarithmic trend** in the number of nodes, from about 6% with 2 nodes to about 15% with 16 and 24 nodes in the plot. A longer window makes it harder for transactions to miss it, so tuning ΔT also limits misalignment in larger networks.

### What the misalignment rate means in practice

Misalignment measures how much each node's list must change to reach the final deterministic order. A rate of 15% means about 15 corrections per 100 transactions on each node. These corrections **do not require communication**: a late transaction's exact position can be computed locally, and only it and its dependents are recalculated.

For a realistic IoT deployment, with many nodes, around 50,000 TPS and a finality of at least 0.5 s, the paper projects a misalignment of about **13%**: in the absolute worst case, 13 recalculations per 100 transactions. On modern hardware that work can typically finish before the first consensus rounds complete (estimated at about 25 ms per round), before even counting independent transactions that need no recalculation. Across the tested range, UGDT stays **under 15% misalignment up to 300,000 TPS** while tolerating jitter.

## Conclusions

- Under suitable conditions on the window ΔT, **global ordering consensus is not necessary**: running unordered with a verification step costs less than agreeing on every order, and ordering failures are compensated in the following windows.
- Only a small subset of transactions ever needs repair, and repairs are **local computation instead of network round trips**. In high-volume blockchains, where network I/O is often the bottleneck, that is the main gain, and caching and hardware acceleration make recalculation faster still.
- Combined with RC-PBFT or similar clustering, the lower communication and computation load lets **lightweight IoT nodes** take part while keeping transaction integrity.
- A deterministic order makes **lock tables local**, removing the network coordination a shared lock table would need.

## Trade-offs and limits

- **Finality versus alignment.** ΔT buys alignment with latency. Short windows misalign badly; long windows delay every transaction.
- **Loose clock synchronization.** Nodes must roughly agree on window boundaries, though the ordering itself does not depend on arrival times.
- **Simulation, not deployment.** The results come from a Go simulator with modeled delays and jitter, not from a running RC-PBFT network.

## Publication

{{< publications bibtex=false >}}
