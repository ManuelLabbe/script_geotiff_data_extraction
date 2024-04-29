import pandas as pd
import rasterio
import numpy as np
from tqdm import tqdm
import os

path_PIRange = r'PIRange-001'
path_rosetta_mean = r'ROSETTA_MEAN'
path_rosetta_sd = r'ROSETTA_SD'
path_SoilMaps_mean = r'SoilMaps_MEAN'
path_Textural_Classes = r'Textural_Classes'
all_paths = [path_PIRange, path_rosetta_mean, path_rosetta_sd, path_SoilMaps_mean, path_Textural_Classes]

def archivos_extraccion(paths):
    archivos = []
    for path in paths:
        for elemento in os.listdir(path):
            ruta_archivo = os.path.join(path, elemento)
            if os.path.isfile(ruta_archivo) and  ruta_archivo.lower().endswith('.tif'):
                archivos.append(fr'{path}/{elemento}')
    return archivos

def tif_extraccion(archivos: list, latlon: pd.DataFrame):
    # archivos: [path1.tif, path2.tif, ...]
    # latlon: [Longitud , Latitud]
    #           x1          y1
    #           x2          y2
    #           ...         ...
    df = pd.DataFrame(latlon)
    for archivo in tqdm(archivos, desc='Archivos'):
        nombre = archivo.split('/')[1]
        valores = []
        #carga = avance / total
        #print(f'Avance de {carga*100}%')
        with rasterio.open(archivo) as dataset:
            for i in tqdm(range(len(latlon)), desc='Coordenadas', leave=False):
                x = latlon.Longitud.iloc[i]
                y = latlon.Latitud.iloc[i]
                #print(f'Coordenadas: {x}, {y}')
                try:
                    x_, y_ = dataset.index(x,y)
                    banda = dataset.read(1)
                    #valor= np.nan

                    valor = banda[x_,y_]
                    #print(f'valor: {valor}')
                    if np.isnan(valor):
                            #print('dentro de if')
                        valor = nan_latlon(dataset=dataset, x=x, y=y)
                except:
                    continue
                        #print(f'Valor post nan_latlon(): {valor}')
                    #print(f'valor except: {valor}')
                valores.append(valor)
        df[nombre] = valores
    # return:
    # df: [Longitud, Latitud, tif1_data, tif2_data, ..., tifn_data]
    #       Long1      Lat1    data1_1    data1_2   ...   data1_n
    #       Long2      Lat2    data2_1    data2_2   ...   data2_n
    #       ...        ...     ...        ...       ...      ...
    return df

def nan_latlon(dataset, x: float , y: float):
    # x += 1 , y += 0
    # x += 0 , y += 1
    # x += 1 , y += 1
    
    # x -= 1 , y -= 0
    # x -= 0 , y -= 1
    # x -= 1 , y -= 1
    arrs = [
        (0.001,.0), (0.001,0.001), (.0,0.001), (-0.001,.0), (-0.001,-0.001), (.0,-0.001)
    ]
    for (py, px) in arrs:
        x_ = x + px
        y_ = y + py
        #print(x_, y_)
        try:
            x__, y__ = dataset.index(x_,y_)
            banda = dataset.read(1)

            valor = banda[x__,y__]
            if not np.isnan(valor):
                return valor
        except:
            continue
    return np.nan

if __name__ == '__main__':
    archivos = archivos_extraccion(all_paths)
    df = pd.read_csv('raw_data_0_01')
    new_col = tif_extraccion(archivos=archivos,latlon=df)
    new_col.to_csv('tif_data_nan_function_0_01')