from wsgiref.simple_server import make_server
from tg import response
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from setUp.myTables import EmergencyCall, MunicipalityUrgency, engine
from setUp.municipalities import municipalities
from setUp.urgencyRatingWeights import num_call_weight, urg_weight, stat_weight, max_calls
from setUp.config import config

def setUpMunicipalityUrgencyRating():
    Session = sessionmaker(bind=engine)
    try:
        with Session() as newSession:
            for municipality in municipalities:
                new_municipality = MunicipalityUrgency(municipality=municipality, urgency_rating=0)
                newSession.add(new_municipality)

            newSession.commit()
            newSession.close()
    except IntegrityError:
        with Session() as newSession:
            for municipality in municipalities:
                curMun = newSession.query(MunicipalityUrgency).filter_by(municipality=municipality).first()
                calls = newSession.query(EmergencyCall).filter_by(municipality=municipality).all()
                num_call_norm = len(calls)/max_calls
                urg_norm = 0
                stat_norm = 0
                for call in calls:
                    urg_norm += call.urgency/4
                    if call.status == "Arrived":
                        stat_norm += 1/4
                    elif call.status == "Seen":
                        stat_norm += 2/4
                    elif call.status == "Not seen":
                        stat_norm += 3/4
                    elif call.status == "NeedHelp":
                        stat_norm += 3/4
                    elif call.status == 'NeedCriticalHelp':
                        stat_norm += 1
                urg_rating = (num_call_norm*num_call_weight)+(urg_norm*urg_weight)+(stat_norm*stat_weight)
                curMun.urgency_rating = urg_rating
                newSession.commit()
                newSession.close()        
    except Exception as e:
                # Handle any exceptions (e.g., file not found, parsing error)
        response.status_code = 500
        #return {'error': str(e)}

if __name__ == '__main__':
    setUpMunicipalityUrgencyRating()
 # Serve the newly configured web application.
    print("Serving on port 8080...")
    httpd = make_server('', 8080, config.make_wsgi_app())
    httpd.serve_forever()