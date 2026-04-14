# exchange-core

## Project Overview

`exchange-core` is a high-performance, open-source market exchange core written in Java. It implements an orders matching engine, risk control and accounting module, disk journaling and snapshots module, and trading/admin/reports API. The project is designed for HFT (high-frequency trading) workloads with a target of sub-millisecond latency under millions of operations per second.

Key capabilities:
- Orders matching engine with two order book implementations: "Naive" (simple) and "Direct" (performance-optimized).
- Risk control and accounting (direct-exchange and margin-trade modes per symbol).
- Event-sourcing with disk journaling, journal replay, state snapshots, and LZ4 compression.
- Lock-free and contention-free matching and risk control algorithms.
- No floating-point arithmetic; all calculations use integer arithmetic to avoid loss of significance.
- Pipelined multi-core processing based on the LMAX Disruptor pattern.

## Technology Stack

- **Language:** Java 8 (source and target compatibility set in `pom.xml`)
- **Build Tool:** Apache Maven
- **Concurrency Framework:** LMAX Disruptor 3.4.2
- **Collections:** Eclipse Collections 11.0.0, exchange.core2:collections 0.5.1
- **Serialization / Journaling:** OpenHFT Chronicle-Wire 2.19.1, LZ4 Java 1.8.0
- **Low-Latency Utilities:** Real Logic Agrona 1.15.1, OpenHFT Affinity 3.2.2
- **Thread Affinity:** JNA / JNA-Platform 5.11.0
- **Code Generation:** Project Lombok 1.18.24
- **Logging:** SLF4J 1.7.36, Logback (test scope only)
- **Testing:** JUnit 5 (Jupiter) 5.8.2, Mockito 4.5.1, Hamcrest 1.3, Cucumber 7.2.3, HDRHistogram 2.1.12

## Architecture

The core runtime is built around a single LMAX Disruptor ring buffer (`OrderCommand`). Commands flow through a fixed pipeline of event handlers:

1. **Grouping Processor (G)** — groups and routes commands.
2. **Journaling (J)** *(optional, parallel)* — writes commands to disk journal for event sourcing.
3. **Risk Hold (R1)** *(sharded, parallel)* — pre-processes risk checks (holds funds/positions).
4. **Matching Engine (ME)** *(sharded, parallel)* — executes order placement, cancellation, move, and matching logic per symbol.
5. **Risk Release (R2)** *(sharded, after ME)* — releases or commits risk holds after matching.
6. **Results Handler (E)** — finalizes the command and emits results to the consumer and API futures.

Matching engines and risk engines are horizontally sharded by `symbolId` and `uid` respectively. The number of shards is configurable via `PerformanceConfiguration`. The `ExchangeCore` class wires all processors together during construction and exposes `ExchangeApi` for publishing commands.

### Key Packages

- `exchange.core2.core` — `ExchangeCore`, `ExchangeApi`, `SimpleEventsProcessor`, `IEventsHandler`.
- `exchange.core2.core.common` — Shared data structures (`OrderCommand`, `CoreSymbolSpecification`, etc.), API command DTOs (`api.*`), report queries/results (`api.reports`), enums, and configuration classes (`config.*`).
- `exchange.core2.core.orderbook` — `IOrderBook` interface and implementations: `OrderBookNaiveImpl`, `OrderBookDirectImpl`, `OrderBookEventsHelper`, `OrdersBucketNaive`.
- `exchange.core2.core.processors` — Disruptor event handlers: `GroupingProcessor`, `MatchingEngineRouter`, `RiskEngine`, `ResultsHandler`, `TwoStepMasterProcessor`, `TwoStepSlaveProcessor`, `SharedPool`, `BinaryCommandsProcessor`, `UserProfileService`, `SymbolSpecificationProvider`.
- `exchange.core2.core.processors.journaling` — Serialization and journaling: `ISerializationProcessor`, `DiskSerializationProcessor`, `DummySerializationProcessor`, descriptors.
- `exchange.core2.core.utils` — Utility classes for serialization and arithmetic.

## Build and Test Commands

Standard Maven lifecycle:

```bash
# Compile and run all tests
mvn clean verify

# Install into local Maven repository
mvn install

# Run only integration tests (matches IT*.java and *IntegrationTest.java)
mvn -Pit clean verify
```

Specific performance test suites (run individually, they are not part of the default `verify` cycle):

```bash
# Latency benchmark
mvn -Dtest=PerfLatency#testLatencyMargin test

# Throughput benchmark
mvn -Dtest=PerfThroughput#testThroughputMargin test

# Hiccups test
mvn -Dtest=PerfHiccups#testHiccups test

# Serialization / persistence benchmark
mvn -Dtest=PerfPersistence#testPersistenceMargin test
```

Example usage test:

```bash
mvn -Dtest=ITCoreExample test
```

## Testing Strategy

The project uses a layered testing approach:

- **Unit tests** — Located in `src/test/java/exchange/core2/core/orderbook/` and `src/test/java/exchange/core2/core/`. They test order book implementations and small components in isolation.
- **Integration tests** — Located in `src/test/java/exchange/core2/tests/integration/`. Class names start with `IT`. They test end-to-end exchange behavior: basic trading, fees (exchange and margin), rejection handling, stress scenarios, and latency regression checks.
- **Performance tests** — Located in `src/test/java/exchange/core2/tests/perf/`. Class names start with `Perf`. These measure latency, throughput, hiccups, and journaling overhead. They use HDRHistogram for latency reporting.
- **Cucumber BDD tests** — Feature files live in `src/test/resources/exchange/core2/tests/features/`. Step definitions are in `src/test/java/exchange/core2/tests/steps/`. There are dedicated runner classes (`RunCukeNaiveTests`, `RunCukesDirectLatencyTests`, `RunCukesDirectThroughputTests`) that bind Cucumber to the JUnit Platform.
- **Example / smoke test** — `ITCoreExample` demonstrates the public API for creating symbols, users, deposits, orders, and reports.

Test utilities (`src/test/java/exchange/core2/tests/util/`):
- `ExchangeTestContainer` — encapsulates creating and tearing down an `ExchangeCore` instance with common configurations.
- `TestOrdersGenerator` / `TestOrdersGeneratorConfig` / `TestOrdersGeneratorSession` — generate randomized order streams for stress and performance tests.
- `LatencyTestsModule`, `ThroughputTestsModule`, `PersistenceTestsModule`, `JournalingTestsModule` — reusable benchmark harnesses.

## Configuration

The behavior of the exchange is controlled by `ExchangeConfiguration`, which is composed of several sub-configurations:

- `OrdersProcessingConfiguration` — order types, fees, margin settings.
- `PerformanceConfiguration` — number of matching engine shards, number of risk engine shards, ring buffer size, wait strategy, thread factory, and order book factory selection.
- `InitialStateConfiguration` — how to initialize or restore state on startup (from journal replay or snapshot).
- `ReportsQueriesConfiguration` — settings for report generation.
- `LoggingConfiguration` — logging behavior.
- `SerializationConfiguration` — journaling and snapshot paths, enable/disable flags, and `ISerializationProcessor` factory.

Typical construction pattern:

```java
ExchangeConfiguration conf = ExchangeConfiguration.defaultBuilder().build();
ExchangeCore exchangeCore = ExchangeCore.builder()
    .resultsConsumer(eventsProcessor)
    .exchangeConfiguration(conf)
    .build();
exchangeCore.startup();
ExchangeApi api = exchangeCore.getApi();
```

## Code Style Guidelines

- Use **Project Lombok** heavily (`@Builder`, `@Getter`, `@Slf4j`, `@RequiredArgsConstructor`, etc.). Generated getters and builders are the norm.
- Source code uses **Apache License 2.0** headers.
- Primitive collections from **Eclipse Collections** and **Agrona** are preferred over standard Java collections in hot paths to reduce GC pressure.
- No floating-point arithmetic in core business logic; use `long` and scaled integer arithmetic.
- Avoid creating transient objects in the disruptor pipeline. Object pooling (`SharedPool`, `ObjectsPool`) is used in matching and risk engines.
- The `OrderCommand` event object is mutable and reused across the ring buffer. Handlers mutate it in place to communicate downstream.

## Security and Correctness Considerations

- **Determinism:** Matching engine and risk control operations are atomic and deterministic. Given the same sequence of commands, the state is exactly reproducible.
- **No floating point:** All monetary and price calculations are performed with integer arithmetic to prevent rounding errors.
- **Event sourcing:** Every mutating command can be journaled to disk, enabling full audit trails and crash recovery via replay.
- **Snapshots:** The system supports state snapshots (`PERSIST_STATE_MATCHING` / `PERSIST_STATE_RISK`) for fast recovery without replaying the entire journal.
- **Thread safety:** The disruptor pipeline guarantees single-threaded access per shard within each stage. No locks are held during matching or risk processing.

## CI and Deployment

- Travis CI is configured in `.travis.yml` to run `mvn clean verify` on Oracle JDK 8.
- The Maven `pom.xml` includes profiles for:
  - Default build with delomboked sources and Javadoc generation.
  - Integration-test profile (`-Pit`).
  - Release signing (`-DperformRelease=true`) and deployment to Maven Central via OSSRH (`https://oss.sonatype.org/`).

## Useful Files for Orientation

- `pom.xml` — Dependencies, plugins, profiles, and build configuration.
- `src/main/java/exchange/core2/core/ExchangeCore.java` — Disruptor wiring and lifecycle.
- `src/main/java/exchange/core2/core/ExchangeApi.java` — Public API for submitting commands asynchronously.
- `src/main/java/exchange/core2/core/common/config/ExchangeConfiguration.java` — Central configuration object.
- `src/test/java/exchange/core2/tests/examples/ITCoreExample.java` — Minimal end-to-end example.
