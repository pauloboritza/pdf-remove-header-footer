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
        
        coordinates = {'x0': [], 'y0': [], 'x1': [], 'y1': []}
        for page in document:
            blocks = page.get_text('blocks')
            for block in blocks:
                coordinates['x0'].append(block[0])
                coordinates['y0'].append(block[1])
                coordinates['x1'].append(block[2])
                coordinates['y1'].append(block[3])
        
        df = pd.DataFrame(coordinates)
        
        quantile = 0.15
        upper = np.floor(df['y0'].quantile(1 - quantile))
        lower = np.ceil(df['y1'].quantile(quantile))
                
        hff = 0.76 #Ref: 0.8 ajuste para baixo caso ainda esteja aparecendo o cabeçalho e rodapé, ou para cima se estiver cortando partes do texto
        min_clust = int(np.floor(n_pages * hff))
        
        if min_clust < 2:
            min_clust = 2
        
        hdbscan = HDBSCAN(min_cluster_size=min_clust)
        df['clusters'] = hdbscan.fit_predict(df)
        
        df_group = df.groupby('clusters').agg(avg_y0=('y0','mean'), avg_y1=('y1','mean'),
                                            std_y0=('y0','std'), std_y1=('y1','std'),
                                            max_y0=('y0','max'), max_y1=('y1','max'),
                                            min_y0=('y0','min'), min_y1=('y1','min'),
                                            cluster_size=('clusters','count'), avg_x0=('x0', 'mean')).reset_index()
        df_group = df_group.sort_values(['avg_y0', 'avg_y1'], ascending=[True, True])
        
        std = 0 
        footer = np.floor(df_group[(np.floor(df_group['std_y0']) == std) & (np.floor(df_group['std_y1']) == std) & (df_group['min_y0'] >= upper) & (df_group['cluster_size'] <= n_pages)]['min_y0'].min())
        header = np.ceil(df_group[(np.floor(df_group['std_y0']) == std) & (np.floor(df_group['std_y1']) == std) & (df_group['min_y1'] <= lower) & (df_group['cluster_size'] <= n_pages)]['min_y1'].max())
        
        return header, footer

    def save_processed_pdf(self):
        header, footer = self.predict_hf()
        doc = fitz.open(self.pdf_path)

        for page in doc:
            blocks = page.get_text('blocks')
            for block in blocks:
                rect = fitz.Rect(block[:4])

                if block[6] == 0:  # Bloco de texto
                    if rect.y0 < header or rect.y1 > footer:
                        # Marcar cabeçalhos e rodapés para remoção
                        page.add_redact_annot(rect, fill=(1, 1, 1))

                elif block[6] > 0:  # Bloco de imagem ou outro tipo
                    if not (rect.y0 < header or rect.y1 > footer):
                        # Compactar a imagem ao inseri-la novamente
                        img = page.get_image(block[6])
                        page.insert_image(rect, stream=img['image'], keep_proportion=True, quality=75) #Aqui ajusta a qualidade das imagens

            # Aplicar as redações marcadas
            page.apply_redactions()

        # Salvar o PDF com otimização para reduzir o tamanho
        doc.save(self.pdf_path_out, deflate=True, garbage=4)
        doc.close()
        print(f"PDF processado salvo em: {self.pdf_path_out}")

    def run(self):
        self.save_processed_pdf()




