
from flask import Flask, request, send_file
from flask_cors import CORS
import fitz  # PyMuPDF
import os
import uuid
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A6

app = Flask(__name__)
CORS(app)  # Libera CORS para qualquer origem

@app.route("/")
def index():
    return "Hello, mundo PDF!"

@app.route("/cortar", methods=["POST"])
def cortar_pdf():
    if "file" not in request.files:
        return "Nenhum arquivo enviado", 400

    file = request.files["file"]
    if file.filename == "":
        return "Arquivo inválido", 400

    # Criar arquivo temporário
    temp_input = f"/tmp/{uuid.uuid4()}.pdf"
    file.save(temp_input)

    doc = fitz.open(temp_input)
    imagens = []

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        temp_img_path = f"/tmp/page_{uuid.uuid4()}.png"
        pix.save(temp_img_path)
        imagens.append(temp_img_path)

    # Gerar PDF 100x150 mm (tamanho etiqueta)
    temp_output = f"/tmp/convertido_{uuid.uuid4()}.pdf"
    c = canvas.Canvas(temp_output, pagesize=landscape(A6))

    for img_path in imagens:
        c.drawImage(img_path, 0, 0, width=landscape(A6)[0], height=landscape(A6)[1])
        c.showPage()
        os.remove(img_path)

    c.save()
    os.remove(temp_input)
    return send_file(temp_output, as_attachment=True, download_name="etiquetas_convertidas.pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

