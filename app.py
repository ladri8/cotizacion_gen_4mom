from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

app = Flask(__name__)


def generar_pdf(datos):
    # Crear un buffer para el PDF
    buffer = BytesIO()

    # Crear el PDF
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Cotización de Propiedad")

    # Fuente y tamaño
    pdf.setFont("Helvetica", 12)

    # Título
    pdf.drawString(50, 750, "Cotización de Propiedad")

    # Información del cliente y vendedor
    pdf.drawString(50, 720, f"Fecha: {datos['fecha']}")
    pdf.drawString(50, 700, f"Cliente: {datos['nombre_cliente']}")
    pdf.drawString(50, 680, f"Vendedor: {datos['nombre_vendedor']}")

    # Detalles de la cotización
    pdf.drawString(50, 650, "Detalles de la Cotización:")
    pdf.drawString(
        50, 630, f"• Valor de la propiedad: ${datos['valor_propiedad']:,.2f}"
    )
    pdf.drawString(50, 610, f"• Valor del pie: ${datos['pie']:,.2f}")
    pdf.drawString(50, 590, f"• Plazo: {datos['plazo_meses']} meses")

    # Resultados
    pdf.drawString(50, 570, "Resultados:")
    pdf.drawString(50, 550, f"► Cuota mensual: ${datos['cuota_mensual']:,.2f}")

    # Finalizar el PDF
    pdf.showPage()
    pdf.save()

    # Mover el buffer al inicio
    buffer.seek(0)
    return buffer


@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    error = None

    if request.method == "POST":
        try:
            nombre_cliente = request.form["nombre_cliente"]
            nombre_vendedor = request.form["nombre_vendedor"]

            # Limpiar y validar el valor de la propiedad
            valor_propiedad_str = (
                request.form["valor_propiedad"].replace(".", "").replace(",", "")
            )
            if not valor_propiedad_str.replace(".", "").isdigit():
                raise ValueError("El valor de la propiedad no es un número válido.")
            valor_propiedad = float(valor_propiedad_str)

            # Limpiar y validar el valor del pie
            pie_str = request.form["pie"].replace(".", "").replace(",", "")
            if not pie_str.replace(".", "").isdigit():
                raise ValueError("El pie no es un número válido.")
            pie = float(pie_str)

            # Validar la tasa de interés
            tasa_mensual_str = request.form["tasa_mensual"]
            if not tasa_mensual_str.replace(".", "").isdigit():
                raise ValueError("La tasa de interés no es un número válido.")
            tasa_mensual = float(tasa_mensual_str)

            # Validar el plazo
            plazo_meses_str = request.form["plazo_meses"]
            if not plazo_meses_str.isdigit():
                raise ValueError("El plazo no es un número válido.")
            plazo_meses = int(plazo_meses_str)

            fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            # Calcular la cuota
            saldo_restante = valor_propiedad - pie
            interes_total = saldo_restante * (tasa_mensual / 100) * plazo_meses
            total_pagar = saldo_restante + interes_total
            cuota_mensual = total_pagar / plazo_meses

            resultado = {
                "nombre_cliente": nombre_cliente,
                "nombre_vendedor": nombre_vendedor,
                "valor_propiedad": int(valor_propiedad),
                "pie": int(pie),
                "plazo_meses": plazo_meses,
                "fecha": fecha,
                "saldo_restante": int(saldo_restante),
                "cuota_mensual": int(cuota_mensual),
            }

            # Generar PDF
            pdf_buffer = generar_pdf(resultado)
            return send_file(
                pdf_buffer, as_attachment=True, download_name="cotizacion.pdf"
            )

        except ValueError as e:
            error = str(e)
        except Exception as e:
            error = f"Error inesperado: {str(e)}"

    return render_template("index.html", resultado=resultado, error=error)


if __name__ == "__main__":
    app.run(debug=True)
