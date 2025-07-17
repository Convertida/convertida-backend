
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait
from reportlab.lib.units import mm
from pdf2image import convert_from_bytes
from io import BytesIO
from PIL import Image
import os

app = Flask(__name__)

@app.route("/cortar", methods=["POST"])
def cortar_etiquetas():
    if 'file' not in request.files:
        return jsonify({"error": "Arquivo não enviado."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nome do arquivo inválido."}), 400

    try:
        pdf_bytes = file.read()
        images = convert_from_bytes(pdf_bytes, dpi=300)

        etiqueta_w, etiqueta_h = 100 * mm, 150 * mm
        writer = PdfWriter()

        for img in images:
            w, h = img.size
            cortes = [
                (0, 0, w // 2, h // 2),
                (w // 2, 0, w, h // 2),
                (0, h // 2, w // 2, h),
                (w // 2, h // 2, w, h),
            ]

            for left, top, right, bottom in cortes:
                etiqueta = img.crop((left, top, right, bottom))
                buffer_img = BytesIO()
                etiqueta.save(buffer_img, format="PNG")
                buffer_img.seek(0)

                packet = BytesIO()
                c = canvas.Canvas(packet, pagesize=portrait((etiqueta_w, etiqueta_h)))
                c.drawImage(buffer_img, 0, 0, width=etiqueta_w, height=etiqueta_h)
                c.save()

                packet.seek(0)
                new_pdf = PdfReader(packet)
                writer.add_page(new_pdf.pages[0])

        output = BytesIO()
        writer.write(output)
        output.seek(0)

        return send_file(output, download_name="etiquetas_convertidas.pdf", as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "API Convertida rodando com sucesso!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


