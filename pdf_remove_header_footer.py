import fitz
import numpy as np
import pandas as pd
from sklearn.cluster import HDBSCAN

class PDFRemoveHeaderFooter:
    def __init__(self, pdf_path, pdf_path_out):
        self.pdf_path = pdf_path
        self.pdf_path_out = pdf_path_out
    
    def predict_hf(self):
        document = fitz.open(self.pdf_path)
        n_pages = document.page_count

        if n_pages == 1:
            document.insert_file(self.pdf_path)
        
        # Coletar Y normalizado para o cluster
        coordinates = {'y0': [], 'y1': []} 
        
        for page in document:
            page_height = page.rect.height
            blocks = page.get_text('blocks')
            for block in blocks:
                # Normalizar coordenadas (0.0 a 1.0)
                coordinates['y0'].append(block[1] / page_height)
                coordinates['y1'].append(block[3] / page_height)
        
        df = pd.DataFrame(coordinates)
        
        # Aumentada a área de busca para 10% da página
        quantile = 0.10
        # Quantiles baseados nas proporções (0-1)
        upper = df['y0'].quantile(1 - quantile)
        lower = df['y1'].quantile(quantile)
                
        # Reduzido para capturar headers/footers que aparecem em poucas páginas
        hff = 0.75 
        min_clust = int(np.floor(n_pages * hff))
        
        if min_clust < 2:
            min_clust = 2
        
        # Clusterizar base apenas na posição vertical normalizada
        hdbscan = HDBSCAN(min_cluster_size=min_clust, allow_single_cluster=True)
        df['clusters'] = hdbscan.fit_predict(df[['y0', 'y1']])
        
        df_group = df.groupby('clusters').agg(avg_y0=('y0','mean'), avg_y1=('y1','mean'),
                                            std_y0=('y0','std'), std_y1=('y1','std'),
                                            max_y0=('y0','max'), max_y1=('y1','max'),
                                            min_y0=('y0','min'), min_y1=('y1','min'),
                                            cluster_size=('clusters','count')).reset_index()
        
        # Tratar NaN nos desvios padrão
        df_group['std_y0'] = df_group['std_y0'].fillna(0)
        df_group['std_y1'] = df_group['std_y1'].fillna(0)

        df_group = df_group.sort_values(['avg_y0', 'avg_y1'], ascending=[True, True])
        
        # Tolerância para variação na posição relativa
        std_tol = 0.01 
        
        potential_footers = df_group[
            (df_group['std_y0'] <= std_tol) & 
            (df_group['std_y1'] <= std_tol) & 
            (df_group['min_y0'] >= upper)
        ]
        
        potential_headers = df_group[
            (df_group['std_y0'] <= std_tol) & 
            (df_group['std_y1'] <= std_tol) & 
            (df_group['min_y1'] <= lower)
        ]
        
        # Retorna proporções (0.0 - 1.0)
        footer_ratio = potential_footers['min_y0'].min() if not potential_footers.empty else 1.0
        header_ratio = potential_headers['min_y1'].max() if not potential_headers.empty else 0.0
        
        return header_ratio, footer_ratio

    def save_processed_pdf(self):
        header_ratio, footer_ratio = self.predict_hf()
        doc = fitz.open(self.pdf_path)

        for page in doc:
            page_height = page.rect.height
            # Calcula limites absolutos para esta página
            header = header_ratio * page_height
            footer = footer_ratio * page_height

            blocks = page.get_text('blocks')
            for block in blocks:
                rect = fitz.Rect(block[:4])

                if block[6] == 0:  # Bloco de texto
                    if rect.y0 < header or rect.y1 > footer:
                        page.add_redact_annot(rect, fill=(1, 1, 1))

                elif block[6] > 0:  # Bloco de imagem ou outro tipo
                    if not (rect.y0 < header or rect.y1 > footer):
                        img = page.get_image(block[6])
                        page.insert_image(rect, stream=img['image'], keep_proportion=True, quality=75)

            page.apply_redactions()

        doc.save(self.pdf_path_out, deflate=True, garbage=4)
        doc.close()
        print(f"PDF processado salvo em: {self.pdf_path_out}")

    def run(self):
        self.save_processed_pdf()




