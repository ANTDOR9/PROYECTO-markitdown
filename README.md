# MarkItDown (versión con interfaz gráfica)

Convierte documentos a Markdown: PDF, Word, PowerPoint, Excel, HTML, CSV, JSON, XML, EPUB, ZIP, imágenes y más.

> Proyecto original: [microsoft/markitdown](https://github.com/microsoft/markitdown) (licencia MIT).
> Este repositorio es una copia personal con una interfaz gráfica añadida.
> El README original en inglés está en [el proyecto de Microsoft](https://github.com/microsoft/markitdown#readme).

## Opción 1: usar el programa (sin terminal)

1. Instala [Python 3.10 o superior](https://www.python.org/downloads/) (marca **Add Python to PATH**).
2. Haz doble clic en **`construir_exe.bat`** (solo la primera vez, tarda unos minutos).
3. Abre **`dist\MarkItDown.exe`**. Ya puedes moverlo a donde quieras.

Dentro del programa:

1. Pulsa **Agregar archivos…** (o arrástralos a la ventana).
2. Pulsa **Convertir**.
3. Elige un archivo de la lista para ver el resultado, luego **Copiar** o **Guardar como .md…**.
   Con varios archivos usa **Guardar todo…**.

## Opción 2: desde la terminal

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e "packages/markitdown[all,gui]"
```

Abrir la ventana:

```bash
markitdown-gui
```

Convertir un archivo directamente:

```bash
markitdown archivo.pdf -o archivo.md
```

## Problemas comunes

| Mensaje | Solución |
|---|---|
| «Falta una dependencia opcional» | `pip install "markitdown[all]"` |
| «Formato no compatible» | Ese tipo de archivo no está soportado |
| `python` no se reconoce | Reinstala Python marcando **Add Python to PATH** |
| El `.exe` tarda en abrir | Es normal la primera vez; se descomprime en segundo plano |

## Seguridad

MarkItDown lee archivos con los permisos de tu usuario. Convierte solo archivos en los que confíes.

## Licencia

MIT, igual que el proyecto original (ver `LICENSE`).
