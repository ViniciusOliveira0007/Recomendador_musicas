def descrever(r):
    partes = [f"{r['playlist_genre']} song, {r['playlist_subgenre']} style, by {r['track_artist']}"]

    partes.append("high energy" if r["energy"] > 0.7
                  else "low energy, calm" if r["energy"] < 0.4
                  else "moderate energy")
    partes.append("very danceable" if r["danceability"] > 0.7
                  else "not very danceable" if r["danceability"] < 0.4
                  else "danceable")
    partes.append("happy, positive mood" if r["valence"] > 0.6
                  else "sad, melancholic mood" if r["valence"] < 0.35
                  else "neutral mood")
    partes.append("fast tempo" if r["tempo"] > 125
                  else "slow tempo" if r["tempo"] < 90
                  else "medium tempo")
    if r["acousticness"] > 0.6:
        partes.append("acoustic")
    if r["instrumentalness"] > 0.5:
        partes.append("instrumental")

    return ", ".join(partes) + "."


def adicionar_descricao(df):
    df["descricao"] = df.apply(descrever, axis=1)
    return df