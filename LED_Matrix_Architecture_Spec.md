
# LED Matrix Project Architecture & Design Specification

## 1. System Overview

This project controls an LED matrix system using a modular, layered architecture that separates interface definitions, 
hardware abstractions, and high-level operations. The design accommodates both real and mocked hardware, 
supports future scalability, and enforces clear boundaries between components.

## 2. Design Principles & Assumptions

- **Interface Segregation**: Abstract interfaces define core behaviors.
- **Hardware Abstraction**: All hardware interactions are mediated via HALs (Hardware Abstraction Layers).
- **Single Responsibility**: Each module has a focused responsibility.
- **Configurability**: The matrix configuration is defined through a standard dictionary-based format.

## 3. Key Components

### 📁 `interfaces/`
Defines abstract base classes for:

- `led.py`: LED behavior (e.g., `on()`, `off()`, `set_color()`)
- `hardware.py`: Hardware communication interface
- `matrix.py`: Matrix-level operations like `fill()`, `clear()`, etc.

### 📁 `models/`
Concrete implementations of `interfaces/` for logic-layer behavior, separated from direct hardware.

### 📁 `hardware/`
Implements various HALs for:

- `mock_hal.py`: Simulated environment for testing
- `pca9685_hal.py`: I2C-based PWM controller
- `rpi_gpio_hal.py`: Raspberry Pi GPIO output

### 📁 `matrix/`
Central logic managing the grid of LEDs:

- `matrix.py`: Coordinates LEDs and their behavior
- Implements initialization from a config matrix only (no row/col/controller trio)
- Each LED is represented by a `HybridLEDController` that binds location and controller

### 📁 `operations/`
Manages high-level behaviors:

- `animation_manager.py`: Timing-based animation sequencing
- `base_patterns.py`: Abstract classes for animations
- `patterns/`: Library of effects (e.g., fade, wave, chase)

### 📁 `tests/`
Tests organized by abstraction layer:

- `tests/unit/`: Logic layer (e.g., LED, pattern behavior)
- 'tests/integration/': Test integration of code with live hardware
- `tests/matrix/`: Matrix configuration and operations
- `tests/operations/`: End-to-end execution of patterns on matrix

## 4. Architectural Decisions

- **LEDMatrix**: Must be initialized with a configuration list of dicts; avoids ambiguity and aligns with `HybridLEDController`.
- **HybridLEDController**: Expects a single configuration dictionary per instance, which includes `row`, `col`, and `controller`.
- **Matrix Config**: Must be created explicitly in tests or app logic; global defaults are discouraged.
- **Mock vs Real**: Controlled via `USE_REAL_HARDWARE` env var, if present, else check for hardware; 
        pytest fixtures automatically choose correct backend.

## 5. Open Issues / Next Steps

- [x] Refactor legacy tests to use config-only matrix initialization
- [x] Create MATRIX_CONFIG for simple and full configurations
- [x] Finalize interface for importing configuration dynamically from file
- [ ] Clarify test responsibility between unit and integration layers
- [ ] (Low Priority) Decide on behavior for partially defined matrices (e.g., non-rectangular)
- [ ] Implement basic patterns with tests


## 6. Change Log (Initial)

- `2025-06-03`: Migrated `LEDMatrix` to require configuration dictionary format.
- `2025-06-03`: Removed row/col/controller trio from `LEDMatrix.__init__`.
- `2025-06-03`: All tests now build matrix config fixtures explicitly.
- `2025-06-03`: HybridLEDController refactored to accept only `config` dict.

---

This document will evolve as design and implementation decisions progress.
