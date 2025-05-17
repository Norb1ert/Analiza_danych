from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Dane
data = {
    "Urząd wojewódzki": [
        "Mazowiecki UW w Warszawie", "Opolski UW w Opolu", "Warmińsko-Mazurski UW w Olsztynie",
        "Śląski UW w Katowicach", "Podlaski UW w Białymstoku", "Dolnośląski UW we Wrocławiu",
        "Wielkopolski UW w Poznaniu", "Małopolski UW w Krakowie", "Podkarpacki UW w Rzeszowie",
        "Zachodniopomorski UW w Szczecinie", "Kujawsko-pomorski UW w Bydgoszczy",
        "Lubuski UW w Gorzowie Wlkp.", "Lubelski UW w Lublinie", "Pomorski UW w Gdańsku",
        "Świętokrzyski UW w Kielcach", "Łódzki UW w Łodzi", "Ogółem"
    ],
    "Wynagrodzenie zasadnicze (brutto)": [
        4587, 4120, 3896, 4299, 4037, 3876, 4228, 4299, 3956, 3913, 4056,
        3998, 3669, 3967, 3727, 3928, 4091
    ],
    "Wynagrodzenie całkowite (brutto)": [
        6631, 6444, 6420, 6319, 6274, 6230, 6169, 6121, 6074, 5877, 5851,
        5753, 5715, 5706, 5650, 5514, 6085
    ]
}

# Utwórz DataFrame i przetwórz
df = pd.DataFrame(data)
df.columns = df.columns.str.strip().str.replace('\xa0', ' ', regex=False)
df['Różnica'] = df['Wynagrodzenie całkowite (brutto)'] - df['Wynagrodzenie zasadnicze (brutto)']

@app.route('/')
def index():
    search = request.args.get('search', '').lower()
    sort_by = request.args.get('sort_by', 'Urząd wojewódzki')
    top_only = request.args.get('top5', 'false') == 'true'

    filtered_df = df.copy()

    # Filtrowanie
    if search:
        filtered_df = filtered_df[filtered_df['Urząd wojewódzki'].str.lower().str.contains(search)]

    # Sortowanie
    if sort_by in filtered_df.columns:
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=False if sort_by == 'Różnica' else True)

    # Top 5
    if top_only:
        filtered_df = filtered_df.head(5)

    # Średnie
    avg_basic = filtered_df["Wynagrodzenie zasadnicze (brutto)"].mean()
    avg_total = filtered_df["Wynagrodzenie całkowite (brutto)"].mean()

    tabela_html = filtered_df.to_html(index=False, classes='table table-striped table-bordered')

    return render_template(
        'index.html',
        tabela=tabela_html,
        avg_basic=round(avg_basic, 2),
        avg_total=round(avg_total, 2),
        search=search,
        sort_by=sort_by,
        top_only=top_only
    )

if __name__ == '__main__':
    app.run(debug=True)
