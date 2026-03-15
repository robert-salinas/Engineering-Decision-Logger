import os
import sys

# Añadir el directorio actual al PYTHONPATH para que reconozca 'src'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.gui import RSEngineeringLoggerGUI

if __name__ == "__main__":
    app = RSEngineeringLoggerGUI()
    app.mainloop()
