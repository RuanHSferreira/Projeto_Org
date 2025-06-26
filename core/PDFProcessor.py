import re
from unidecode import unidecode
import PyPDF2
from .models import GuiaMetadados
import os
import json



class PDFProcessor:

    def __init__(self, caminho):
        self._caminho = caminho
        with open(caminho, 'rb') as file:
            self._reader = PyPDF2.PdfReader(file)
            self._texto = self._reader.pages[0].extract_text()

        self.tipo_doc = re.search(r"Documento de Arrecadação\n(.*)", self._texto).group(1)
        if self.tipo_doc == "de Receitas Federais" or self.tipo_doc == "do eSocial":
            self.dados: GuiaMetadados = self._extrair_pdf_inss()


    def _normalizar_raz_social(self):
        """Remove caracteres especiais e normaliza para ASCII"""
        texto_normalizado = unidecode(self._empresa).upper()
        lp = re.sub(r'[^\w\s]|[\d_]', '', texto_normalizado)
        return re.sub(r'\s+', ' ', lp).strip()

    # Exemplo de extração de dados do PDF - INSS
    def _extrair_pdf_inss(self) -> GuiaMetadados:
        '''
        Returns
            cnpj, Razao Social, MesRef, CodigoGuia, Recalculada
        '''
        
        # Padrões customizáveis (ajuste conforme seus PDFs)
        cnpj = re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", self._texto).group()
        self._empresa = re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\s*(.*)", self._texto).group(1)
        cod_ident_documento = re.search(r"(\S+)Pagar este documento até", self._texto).group(1)
        comp_venc = re.search(r"PA:(\S+)\s+Vencimento:(.+)", self._texto)
        vencimento_up = re.search(r"(\S+)Observações", self._texto).group(1)
        vencimento_down = re.search(r"Pagar até: (\S+)", self._texto).group(1)
        vencimento = vencimento_up if vencimento_up == vencimento_down else None
        valor = re.search(r'Valor:\s*(\d+,\d{1,2})', self._texto).group(1)
        
        if comp_venc == None:
            '''
            Tratamento Para quando for guia do eSocial
            '''
            competencia = re.search(r"PA:(\S+)", self._texto).group(1)
            vencimento_original = re.search(r"Data de Vencimento\n(\d{2}/\d{2}/\d{4})", self._texto).group(1)
        else:
            '''
            INSS - Normal
            '''
            competencia = comp_venc.group(1)
            vencimento_original = comp_venc.group(2)
        
        recalculado = 'Sim' if vencimento != vencimento_original else 'Nao'
        # return {
        #     'CNPJ': cnpj,
        #     'Razao Social': self._normalizar_raz_social(),
        #     'MesRef': competencia,
        #     'CodigoGuia': cod_ident_documento,
        #     'Recalculada': recalculado,
        #     'Valor': valor
        # }
        return GuiaMetadados(cnpj,
                             competencia,
                             vencimento,
                             vencimento_original,
                             valor,
                             cod_ident_documento,
                             self._caminho)

