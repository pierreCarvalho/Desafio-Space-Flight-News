
import requests
import json 
from database import Article, Event, Launch
from sqlalchemy.orm import Session
from database import Base, engine


def buscar_dados():
    request = requests.get("https://api.spaceflightnewsapi.net/v3/articles/")
    artigos = json.loads(request.content)
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)
    for artigo in artigos:
        try:
            article = Article(
                id=artigo["id"],
                title= artigo["title"],
                url= artigo["url"],
                imageUrl= artigo["imageUrl"],
                newsSite= artigo["newsSite"],
                summary= artigo["summary"],
                publishedAt= artigo["publishedAt"],
                featured= artigo["featured"]
                )
            # popular event
            # add it to the session and commit it
            if artigo["launches"]:
                for launch in artigo["launches"]:
                    session.add( Launch(provider=launch["provider"], article_id=article.id ) )
            if artigo["events"]:
                for event in artigo["events"]:
                    session.add( Launch(provider=event["provider"], article_id=article.id  ))
            session.add(article)
            session.commit()
        except Exception as e:
            print(e)
            break
    
    # close the session
    session.close()
if __name__ == '__main__':
    buscar_dados()
