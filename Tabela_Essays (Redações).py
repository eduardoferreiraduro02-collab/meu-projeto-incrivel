class Redacao:
    def __init__(self, titulo, tema, texto_ou_url, status="Pendente"):
        self.titulo = titulo
        self.tema = tema
        self.texto_ou_url = texto_ou_url
        self.status = status

    def __repr__(self):
        return f"[{self.status}] {self.titulo} - Tema: {self.tema}"

# Exemplo de uso:
minha_redacao = Redacao("A IA na Educação", "Tecnologia", "c:/documentos/redacao1.docx")
print(minha_redacao)