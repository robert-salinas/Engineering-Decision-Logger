# 🚀 Engineering Decision Logger (EDL) v0.2.0 - RS Digital Edition

[![Tests and Linting](https://github.com/robert-salinas/Engineering-Decision-Logger/actions/workflows/tests.yml/badge.svg)](https://github.com/robert-salinas/Engineering-Decision-Logger/actions/workflows/tests.yml)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![UI: RS Digital](https://img.shields.io/badge/UI-RS%20Digital-orange)

**EDL** es una herramienta de infraestructura técnica diseñada para eliminar uno de los mayores problemas en el desarrollo de software: la pérdida del **por qué** detrás de las decisiones arquitectónicas. Ahora con una interfaz gráfica nativa (GUI) optimizada para el flujo de trabajo de ingeniería.

---

### ✨ ¿Por qué EDL?

En proyectos complejos, las decisiones técnicas a menudo se pierden. **EDL** resuelve esto proporcionando:

*   🏛️ **Gobernanza de Decisiones:** Un flujo de trabajo formal para documentar ADRs (Architecture Decision Records).
*   �️ **RS Digital Interface:** Nueva interfaz gráfica moderna (Dark/Orange) para una gestión visual y rápida.
*   �🔗 **Trazabilidad con Git:** Cada decisión se vincula automáticamente con el commit actual.
*   🔍 **Memoria Histórica:** Motor de búsqueda integrado para recuperar contexto técnico al instante.
*   🛠️ **Rigor Arquitectónico:** Evaluación estructurada de contextos, soluciones y justificaciones.

---

### 🛠️ Stack Tecnológico

*   **GUI Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (RS Digital Aesthetic)
*   **Base de Datos:** SQLite con [SQLModel](https://sqlmodel.tiangolo.com/)
*   **Templates:** Jinja2 para generación automática de archivos ADR (.md)
*   **Integración:** GitPython para trazabilidad con Git
*   **Automatización:** Scripts PowerShell y Batch para despliegue "One-Click"

---

### 🚀 Instalación y Lanzamiento (Windows)

El proyecto incluye un sistema de arranque automatizado (**RS Project Bootstrap**) que gestiona el entorno virtual y las dependencias por ti.

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/robert-salinas/Engineering-Decision-Logger.git
    cd Engineering-Decision-Logger
    ```

2.  **Lanzar la aplicación:**
    Ejecuta el archivo `run_app.bat` en la raíz del proyecto.
    *   La primera vez, creará el entorno virtual `.venv` e instalará las dependencias.
    *   Creará automáticamente un acceso directo **"RS-EDL"** en tu **Escritorio**.

---

### �️ Uso de la Interfaz RS Digital

*   **Historial Lateral:** Navega rápidamente por todas las decisiones pasadas.
*   **Búsqueda en Tiempo Real:** Filtra decisiones por título o contenido técnico.
*   **Nueva Decisión:** Pulsa el botón naranja `+ Nueva Decisión` para abrir el formulario integrado.
*   **Visualización Detallada:** Consulta el contexto, la solución y la justificación técnica en un layout limpio y profesional.

---

### 📂 Estructura de Documentación

*   [Registros de Decisiones (ADRs)](docs/ADR/): Archivos Markdown generados automáticamente.
*   [Arquitectura del Sistema](docs/ARCHITECTURE.md): Detalles técnicos del motor de EDL.
*   [Ejemplos de Uso](docs/EXAMPLES.md): Casos de uso comunes en ingeniería.

---

### 🤝 Contribución

¡Las contribuciones son bienvenidas! Por favor, consulta nuestra [Guía de Contribución](CONTRIBUTING.md).

---

### ⚖️ Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

Desarrollado con ❤️ por **Robert Salinas** para equipos que valoran la excelencia técnica y el diseño de vanguardia.
