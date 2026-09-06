# ⚡ EV Charging Spain

## Plataforma Inteligente para la Optimización de Infraestructuras de Recarga de Vehículos Eléctricos

Trabajo Fin de Máster desarrollado en el Máster en Data Science, Big Data & Business Analytics.

El proyecto analiza la infraestructura pública de recarga de vehículos eléctricos en España mediante técnicas de análisis de datos, Machine Learning y análisis geoespacial.

🔗 **Aplicación web:**  
https://alicia-ev-charging.streamlit.app/

---

## 🎯 Objetivos

El proyecto persigue cuatro objetivos principales:

- Analizar la distribución actual de la infraestructura de recarga en España.
- Detectar municipios con una mayor necesidad relativa de infraestructura.
- Proponer nuevas localizaciones estratégicas para puntos de recarga.
- Recomendar estaciones existentes al usuario en función de su localización y características de recarga.

---

## 📊 Fuentes de datos

Se han integrado diferentes fuentes públicas:

- **Open Charge Map**: estaciones y conectores de recarga.
- **INE**: información demográfica municipal.
- **CNIG**: límites geográficos municipales.
- **DGT**: parque de vehículos electrificados.
- **OpenStreetMap / Geofabrik**: red viaria y puntos de interés.

La combinación de estas fuentes permite construir una visión territorial y técnica de la infraestructura de recarga.

---

## 🧠 Metodología

El proyecto se ha desarrollado mediante un flujo reproducible dividido en varias etapas:

1. Adquisición de datos.
2. Limpieza y preprocesamiento.
3. Integración geoespacial.
4. Análisis exploratorio.
5. Ingeniería de variables.
6. Análisis territorial de necesidad de infraestructura.
7. Optimización de nuevas localizaciones.
8. Sistema de recomendación de estaciones.
9. Modelos de Machine Learning.
10. Productivización mediante una aplicación web interactiva.

---

## 🤖 Machine Learning

Se han utilizado diferentes técnicas de Machine Learning.

### Aprendizaje supervisado

Se compararon varios modelos para estimar el número de estaciones asociado al perfil demográfico y territorial de cada municipio:

- Dummy Regressor
- Poisson Regressor
- Random Forest Regressor
- HistGradientBoosting Regressor

El modelo Random Forest obtuvo el menor MAE y se utilizó como referencia operativa.

La diferencia entre el número real de estaciones y la estimación del modelo se interpreta como una desviación respecto al patrón aprendido y no como el número exacto de estaciones que deberían instalarse.

### Aprendizaje no supervisado

Se aplicó K-Means para identificar perfiles territoriales similares en función de variables demográficas, de infraestructura y accesibilidad.

Los clusters obtenidos representan perfiles multivariantes y no deben interpretarse únicamente como grupos definidos por tamaño de población.

---

## 📍 Optimización de nuevas localizaciones

Se generaron candidatos de localización a partir de puntos de interés de OpenStreetMap en municipios prioritarios.

Las propuestas se valoraron mediante un índice multicriterio compuesto por:

- 45 % necesidad territorial
- 15 % nivel de electrificación
- 20 % distancia a infraestructura existente
- 10 % accesibilidad a vías principales
- 10 % adecuación del punto de interés

Finalmente se seleccionaron **50 localizaciones estratégicas**, aplicando además una separación mínima de 5 km entre propuestas.

Estas localizaciones representan candidatos estratégicos y no ubicaciones definitivas a nivel de parcela. Una implantación real requeriría incorporar información adicional sobre capacidad eléctrica, propiedad del suelo, costes y restricciones técnicas.

---

## 🔌 Sistema de recomendación

La aplicación permite seleccionar un municipio de origen y buscar estaciones cercanas en función de:

- distancia máxima,
- potencia mínima,
- proximidad,
- potencia disponible.

La información de precios se muestra cuando puede extraerse de los datos originales de Open Charge Map.

---

## 🌐 Aplicación web

La solución se ha productivizado mediante **Streamlit**.

La aplicación contiene cuatro módulos:

- **Inicio**: visión general de la infraestructura.
- **Buscar estación**: recomendación de estaciones existentes.
- **Déficit territorial**: análisis municipal, Machine Learning y clustering.
- **Nuevas localizaciones**: visualización y exploración de las 50 propuestas.

Aplicación desplegada:

👉 https://alicia-ev-charging.streamlit.app/

---

## 🛠️ Tecnologías

- Python
- Pandas
- GeoPandas
- NumPy
- Scikit-learn
- OpenStreetMap
- Streamlit
- Plotly
- Git / GitHub
- Google Colab

---

## 📂 Estructura del proyecto

```text
TFM_EV_Charging/
│
├── app.py
├── app/
├── data/
├── requirements.txt
├── README.md
└── .gitignore
cat > README.md <<'EOF'
# ⚡ EV Charging Spain

## Plataforma Inteligente para la Optimización de Infraestructuras de Recarga de Vehículos Eléctricos

Trabajo Fin de Máster desarrollado en el Máster en Data Science, Big Data & Business Analytics.

El proyecto analiza la infraestructura pública de recarga de vehículos eléctricos en España mediante técnicas de análisis de datos, Machine Learning y análisis geoespacial.

🔗 **Aplicación web:**  
https://alicia-ev-charging.streamlit.app/

---

## 🎯 Objetivos

El proyecto persigue cuatro objetivos principales:

- Analizar la distribución actual de la infraestructura de recarga en España.
- Detectar municipios con una mayor necesidad relativa de infraestructura.
- Proponer nuevas localizaciones estratégicas para puntos de recarga.
- Recomendar estaciones existentes al usuario en función de su localización y características de recarga.

---

## 📊 Fuentes de datos

Se han integrado diferentes fuentes públicas:

- **Open Charge Map**: estaciones y conectores de recarga.
- **INE**: información demográfica municipal.
- **CNIG**: límites geográficos municipales.
- **DGT**: parque de vehículos electrificados.
- **OpenStreetMap / Geofabrik**: red viaria y puntos de interés.

La combinación de estas fuentes permite construir una visión territorial y técnica de la infraestructura de recarga.

---

## 🧠 Metodología

El proyecto se ha desarrollado mediante un flujo reproducible dividido en varias etapas:

1. Adquisición de datos.
2. Limpieza y preprocesamiento.
3. Integración geoespacial.
4. Análisis exploratorio.
5. Ingeniería de variables.
6. Análisis territorial de necesidad de infraestructura.
7. Optimización de nuevas localizaciones.
8. Sistema de recomendación de estaciones.
9. Modelos de Machine Learning.
10. Productivización mediante una aplicación web interactiva.

---

## 🤖 Machine Learning

Se han utilizado diferentes técnicas de Machine Learning.

### Aprendizaje supervisado

Se compararon varios modelos para estimar el número de estaciones asociado al perfil demográfico y territorial de cada municipio:

- Dummy Regressor
- Poisson Regressor
- Random Forest Regressor
- HistGradientBoosting Regressor

El modelo Random Forest obtuvo el menor MAE y se utilizó como referencia operativa.

La diferencia entre el número real de estaciones y la estimación del modelo se interpreta como una desviación respecto al patrón aprendido y no como el número exacto de estaciones que deberían instalarse.

### Aprendizaje no supervisado

Se aplicó K-Means para identificar perfiles territoriales similares en función de variables demográficas, de infraestructura y accesibilidad.

Los clusters obtenidos representan perfiles multivariantes y no deben interpretarse únicamente como grupos definidos por tamaño de población.

---

## 📍 Optimización de nuevas localizaciones

Se generaron candidatos de localización a partir de puntos de interés de OpenStreetMap en municipios prioritarios.

Las propuestas se valoraron mediante un índice multicriterio compuesto por:

- 45 % necesidad territorial
- 15 % nivel de electrificación
- 20 % distancia a infraestructura existente
- 10 % accesibilidad a vías principales
- 10 % adecuación del punto de interés

Finalmente se seleccionaron **50 localizaciones estratégicas**, aplicando además una separación mínima de 5 km entre propuestas.

Estas localizaciones representan candidatos estratégicos y no ubicaciones definitivas a nivel de parcela. Una implantación real requeriría incorporar información adicional sobre capacidad eléctrica, propiedad del suelo, costes y restricciones técnicas.

---

## 🔌 Sistema de recomendación

La aplicación permite seleccionar un municipio de origen y buscar estaciones cercanas en función de:

- distancia máxima,
- potencia mínima,
- proximidad,
- potencia disponible.

La información de precios se muestra cuando puede extraerse de los datos originales de Open Charge Map.

---

## 🌐 Aplicación web

La solución se ha productivizado mediante **Streamlit**.

La aplicación contiene cuatro módulos:

- **Inicio**: visión general de la infraestructura.
- **Buscar estación**: recomendación de estaciones existentes.
- **Déficit territorial**: análisis municipal, Machine Learning y clustering.
- **Nuevas localizaciones**: visualización y exploración de las 50 propuestas.

Aplicación desplegada:

👉 https://alicia-ev-charging.streamlit.app/

---

## 🛠️ Tecnologías

- Python
- Pandas
- GeoPandas
- NumPy
- Scikit-learn
- OpenStreetMap
- Streamlit
- Plotly
- Git / GitHub
- Google Colab

---

## 📂 Estructura del proyecto

```text
TFM_EV_Charging/
│
├── app.py
├── app/
├── data/
├── requirements.txt
├── README.md
└── .gitignore
