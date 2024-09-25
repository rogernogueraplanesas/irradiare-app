<div align="center">
  <img src="docs/images/logo.png" width="65%" height="65%" alt="Irradiare-app-logo">
  <br style="margin-bottom: 0.25em;">
</div>
<br>

# DevTrack app - IrRadiare
![Static Badge](https://img.shields.io/badge/language-python-blue) ![GitHub repo size](https://img.shields.io/github/repo-size/:rogernogueraplanesas/:portugal-weather-analysis) ![GitHub last commit](https://img.shields.io/github/last-commit/:rogernogueraplanesas/:portugal-weather-analysis) <br>

Irradiare's DevTrack App is an internal tool designed to **monitor the performance and efficiency** of the company’s implemented projects over time, utilizing key indicator data. In addition to tracking, the app facilitates **forecasting project outcomes**, enabling the company to optimize the timing of new initiatives based on predicted values for these indicators.<br>
Project impact can be analyzed across **multiple geographical levels**, including parishes, municipalities, districts, and the national level. Additionally, the app supports tracking indicators based on NUTS (Nomenclature of Territorial Units for Statistics) levels.<br>
The app's database is populated with indicator data sourced from [E-REDES](https://e-redes.opendatasoft.com/explore/?sort=modified), [Eurostat](https://ec.europa.eu/eurostat/data/database), [INE](https://www.ine.pt/xportal/xmain?xpid=INE&xpgid=ine_api&INST=322751522), and [The World Bank](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation).

<br>
<br>
<h2>
  <img src="docs/images/requisites.jpg" width="25" height="25" alt="Icon" style="vertical-align: middle;"/> 
  <span style="vertical-align: middle;">Requirements</span>
</h2>

```
pip install -r requirements.txt
```
<br>

<h2 id="summary">
  <img src="sample_images/summary.jpg" width="25" height="25" alt="Icon" style="vertical-align: middle;"/> 
  <span style="vertical-align: middle;">Summary</span>
</h2>

The development of the DevTrack App is driven by Irradiare's **strategic commitment to leveraging data for more informed decision-making**. As the company continues to implement diverse projects, it has become increasingly important to have a precise, data-driven summary of project evolution over time.<br>
By integrating key economic, social, and environmental indicators, the app provides a comprehensive view of project performance and potential.<br>
Furthermore, the ability to forecast these indicators offers the company valuable insights into the future impact of its initiatives, allowing for better prioritization of upcoming projects. This data-backed approach enables the company to assess, with greater accuracy, which projects to bid on next, ensuring more logical, safer, and efficient project selection and execution.<br>
The flexibility to connect various dimensions of performance within the app strengthens decision-making, fostering an optimized, strategic, and long-term perspective for the company's future initiatives.

> SQLite for the database creation (currently).

> As explained in the docs for each data source, many different data retrieval and processing techniques were applied.

<br>
<div align="center">
  <img src="docs/images/irradiare-app-gif.gif" width="85%" height="85%" alt="app-data-pathway">
  <br style="margin-bottom: 0.25em;">
  <sub>DevTrack App's data pathway</sub>
</div>
<br>
