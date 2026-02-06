# 🚀 Engineering Decision Logger (EDL) v0.1.0

[![Tests and Linting](https://github.com/robert-salinas/Engineering-Decision-Logger/actions/workflows/tests.yml/badge.svg)](https://github.com/robert-salinas/Engineering-Decision-Logger/actions/workflows/tests.yml)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

**EDL** es una herramienta de infraestructura técnica diseñada para eliminar uno de los mayores problemas en el desarrollo de software: la pérdida del **por qué** detrás de las decisiones arquitectónicas.

---

### ✨ ¿Por qué EDL?

En proyectos complejos, las decisiones técnicas a menudo se pierden en hilos de Slack, correos o reuniones. **EDL** resuelve esto proporcionando:

*   🏛️ **Gobernanza de Decisiones:** Un flujo de trabajo formal para documentar ADRs (Architecture Decision Records).
*   🔗 **Trazabilidad con Git:** Cada decisión se vincula automáticamente con el commit actual, uniendo el código con su racional.
*   🔍 **Memoria Histórica:** Un motor de búsqueda local para recuperar el contexto de decisiones tomadas hace meses o años.
*   🛠️ **Rigor Arquitectónico:** Obliga al equipo a evaluar pros, contras y consecuencias antes de implementar cambios críticos.

---

### 🛠️ Stack Tecnológico

*   **Lenguaje:** Python 3.11+
*   **CLI Framework:** [Typer](https://typer.tiangolo.com/)
*   **Base de Datos:** SQLite con [SQLModel](https://sqlmodel.tiangolo.com/)
*   **Templates:** Jinja2 para generación de Markdown
*   **Integración:** GitPython para trazabilidad con Git
*   **UI:** Rich para una experiencia de terminal elegante

---

### 🚀 Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/robert-salinas/Engineering-Decision-Logger.git
cd Engineering-Decision-Logger

# Instalar dependencias en modo editable
pip install -e .
```

---

### 🛠️ Uso Básico

```bash
# Registrar una nueva decisión técnica (Modo Interactivo)
edl log

# Listar todas las decisiones registradas
edl list-decisions

# Buscar decisiones por palabras clave
edl search "PostgreSQL"

# Ver el detalle completo de una decisión
edl show 1

# Instalar hooks de Git para automatizar la trazabilidad
edl install-hooks
```

---

### � Documentación

*   [Ejemplos de Uso](docs/EXAMPLES.md)
*   [Guía de Solución de Problemas](docs/TROUBLESHOOTING.md)
*   [Arquitectura del Sistema](docs/ARCHITECTURE.md)
*   [Registros de Decisiones (ADRs)](docs/ADR/)

---

### 🤝 Contribución

¡Las contribuciones son bienvenidas! Por favor, consulta nuestra [Guía de Contribución](CONTRIBUTING.md) y el [Código de Conducta](CODE_OF_CONDUCT.md) antes de empezar.

---

### � Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

Desarrollado con ❤️ por **Robert Salinas** para equipos que valoran la excelencia técnica.
