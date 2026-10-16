"""Punto de entrada. Sin lógica de negocio hasta que se apruebe la arquitectura."""

from water_coordinator import __version__, config


def main() -> None:
    print(f"water-coordinator {__version__} ({config.APP_ENV}) - fase de diseño, sin agentes activos.")


if __name__ == "__main__":
    main()
