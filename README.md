# 🚀 Engineering Decision Logger (EDL) v0.1.0

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

**EDL** es una herramienta de línea de comandos diseñada para ingenieros que necesitan capturar, gestionar y rastrear decisiones técnicas (ADR) de manera profesional, asegurando la trazabilidad y el rigor arquitectónico en cada etapa del desarrollo.

---

### ✨ Características

* 🏛️ **Estándar ADR Profesional:** Documenta el racional de tus decisiones siguiendo el estándar de *Architecture Decision Records*.
* 🔗 **Trazabilidad con Git:** Vincula automáticamente cada decisión con el hash del commit actual para saber exactamente por qué cambió el código.
* 🔍 **Búsqueda Avanzada:** Motor de búsqueda local en SQLite para encontrar rápidamente decisiones pasadas por título, contexto o justificación.
* 🛠️ **Gobernanza Automatizada:** Sistema de hooks pre-commit para garantizar que las decisiones críticas no se pierdan en el flujo de trabajo.

---

### 🚀 Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/robertesteban/Engineering-Decision-Logger.git
cd Engineering-Decision-Logger

# Instalar dependencias en modo editable
pip install -e .
```

---

### 🛠️ Uso Básico

Para gestionar tus decisiones de ingeniería de forma eficiente:

```bash
# Registrar una nueva decisión técnica (Modo Interactivo)
edl log

# Listar todas las decisiones registradas en el historial
edl list

# Buscar decisiones por palabras clave
edl search "SQLite"

# Ver el detalle completo de una decisión específica
edl show 1

# Instalar hooks de Git para automatizar el registro
edl install-hooks
```

---

### 📝 Estructura de Decisiones (ADR)

EDL genera registros estructurados que aseguran la calidad de la documentación técnica:

* **Status:** Estado del ciclo de vida (Proposed, Accepted, Deprecated, Superseded).
* **Context:** Definición del problema y los factores que motivaron la decisión.
* **Decision Drivers:** Factores clave (Rendimiento, Seguridad, Coste) que influyeron en la elección.
* **Rationale:** Justificación objetiva de por qué se eligió la opción ganadora sobre las alternativas.
* **Consequences:** Evaluación de los impactos positivos y negativos resultantes.

**Estados Soportados:**
* **Proposed:** La decisión está en fase de revisión y discusión.
* **Accepted:** La decisión ha sido aprobada e implementada.
* **Deprecated:** La decisión ya no es relevante para el estado actual del proyecto.
* **Superseded:** La decisión ha sido reemplazada por una más reciente (ADR posterior).

---

### 📖 Documentación Adicional

* [Arquitectura y Decisiones de Diseño](docs/ARCHITECTURE.md)
* [Registros de Decisiones del Proyecto (ADRs)](docs/ADR/)
* [Guía de Contribución](https://github.com/robertesteban/Engineering-Decision-Logger)

---

Desarrollado con rigor técnico para equipos que valoran la memoria arquitectónica.
