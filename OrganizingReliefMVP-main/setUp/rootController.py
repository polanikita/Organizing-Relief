from tg import expose, TGController, redirect, response, session 
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import json 
from setUp.myTables import User, EmergencyCall, EmergencyCallsResponses, Orgs, MunicipalityUrgency, Hubs, engine, Chats, MunicipalityChats
from setUp.municipalities import municipalities
from setUp.urgencyRatingWeights import num_call_weight, urg_weight, stat_weight, max_calls
from urllib.parse import unquote_plus


            
#Root Controller
class RootController(TGController):
    @expose("pages/homePage.xhtml")
    def index(self):
        return dict(page='homePage') 
    
    @expose("pages/citizenHome.xhtml")
    def citizenHomePage(self, municipality=None, description=None, location=None, urgency=None):
        
        name = session['name']
        email = session['email']
        Session = sessionmaker(bind=engine)
        dbsession = Session()
        calls = session['calls']
        error_message = ''
        #if form submitted
        if location and municipality and description and urgency:
            permanent_list = []
            if municipality not in municipalities:
                return dict(page='citizenHome', civilian_name=name, error_message ="Form Submision failed! Enter a Municipality in Puerto Rico", calls=permanent_list, municipalityList = municipalities)
            Session = sessionmaker(bind=engine)
            dbsession = Session()

            now = datetime.now()
            emergency_call = EmergencyCall(
                urgency=urgency,
                emergencyDescription=description,
                municipality=municipality,
                extendedLocationInfo =location,                
                date_time_called=now,
                lastUpdated = now,
                user_email = email,
                status = 'Not seen'
            )
            dbsession.add(emergency_call)
            dbsession.commit()
            curMun = dbsession.query(MunicipalityUrgency).filter_by(municipality=municipality).first()
            stat_norm = 0
            if emergency_call.status == "Arrived":
                stat_norm += 1/4
            elif emergency_call.status == "Seen":
                stat_norm += 2/4
            elif emergency_call.status == "Not seen":
                stat_norm += 3/4
            elif emergency_call.status == "NeedHelp":
                stat_norm += 3/4
            elif emergency_call.status == 'NeedCriticalHelp':
                stat_norm += 1

            curMun.urgency_rating += (1/max_calls)*(num_call_weight) + (emergency_call.urgency/4)* (urg_weight)+ (stat_norm)*(stat_weight)
            dbsession.commit()
            date_time = now.strftime("%m/%d/%Y - %H:%M")
            error_message = 'Form successfully submitted: ' + date_time
            dbsession.close()
            currUser = dbsession.query(User).filter_by(email=email).first()
            calls = currUser.children 
            session['calls']= calls
            session.save()
            for call in calls:
                temp_list  = []
                temp_list.append((call.date_time_called.strftime("%m/%d/%Y - %H:%M")))
                temp_list.append(call.emergencyDescription)
                temp_list.append(call.municipality)
                temp_list.append(call.extendedLocationInfo)
                temp_list.append(call.status)
                temp_list.append(call.callId)
                permanent_list.append(temp_list)
            dbsession.close()
            return dict(page='citizenHome', civilian_name=name, error_message =error_message, calls=permanent_list, municipalityList = municipalities)
        dbsession.close()
        if location or municipality or description or urgency:
            error_message = "Fill out all fields. Try again!"
        #else if just loading in home page

        permanent_list = []
        for call in calls:
            temp_list  = []
            temp_list.append((call.date_time_called.strftime("%m/%d/%Y - %H:%M")))
            temp_list.append(call.emergencyDescription)
            temp_list.append(call.municipality)
            temp_list.append(call.extendedLocationInfo)
            temp_list.append(call.status)
            temp_list.append(call.callId)
            permanent_list.append(temp_list)
        return dict(page='citizenHome', civilian_name = name, error_message =error_message, calls=permanent_list, municipalityList = municipalities)


    @expose("pages/citizenSignUpPage.xhtml")
    def citizenSignUpPage(self, name=None, email=None, password=None, confirmPassword=None):
        error_message = ''
        if name and email and password == confirmPassword:
            try:
                new_user = User(email=email, name=name, password=password, orgName='None')
                Session = sessionmaker(bind=engine)
                dbsession = Session()
                dbsession.add(new_user)
                dbsession.commit()
                session['name'] = new_user.name
                session['email'] = new_user.email
                session['calls'] = []
                session.save()
                dbsession.close()
                return redirect("/citizenHomePage")
            except IntegrityError as a:
                error_message = "Email is already in use. Please choose a different email."
                return dict(page='citizenSignUpPage', error_message=error_message)
        else:
            if (password != confirmPassword):
                error_message = 'Passwords do not match. Try again!'
            elif(name or email or password or confirmPassword):
                error_message = "Fill out all fields. Try again!"
            return dict(page='citizenSignUpPage', error_message=error_message)
        
    
    @expose("pages/providerHome.xhtml")
    def providerHomePage(self, municipality=None, description=None, location=None, urgency=None):
        email = session['email']
        calls = session['calls']
        name = session['name']
        error_message = ''
        if location and municipality and description and urgency:
            permanent_list = []
            if municipality not in municipalities:
                return dict(page='providerHome', civilian_name=name, error_message ="Form Submision failed! Enter a Municipality in Puerto Rico", calls=permanent_list, user_email=email, municipalityList = municipalities)

            Session = sessionmaker(bind=engine)
            dbsession = Session()
            currUser = dbsession.query(User).filter_by(email=email).first()

            now = datetime.now()
            emergency_call = EmergencyCall(
                urgency=urgency,
                emergencyDescription=description,
                municipality=municipality,
                extendedLocationInfo =location,                
                date_time_called=now,
                lastUpdated = now,
                user_email = email,
                status = 'Not seen',
            )
            dbsession.add(emergency_call)
            dbsession.commit()

            curMun = dbsession.query(MunicipalityUrgency).filter_by(municipality=municipality).first()
            stat_norm = 0
            if emergency_call.status == "Arrived":
                stat_norm += 1/4
            elif emergency_call.status == "Seen":
                stat_norm += 2/4
            elif emergency_call.status == "Not seen":
                stat_norm += 3/4
            elif emergency_call.status == "NeedHelp":
                stat_norm += 3/4
            elif emergency_call.status == 'NeedCriticalHelp':
                stat_norm += 1
            curMun.urgency_rating += (1/max_calls)*(num_call_weight) + (emergency_call.urgency/4)*(urg_weight)+ (stat_norm)*(stat_weight)
            dbsession.commit()

            date_time = now.strftime("%m/%d/%Y - %H:%M")
            error_message = 'Form successfully submitted: ' + date_time
            calls = currUser.children 
            session['calls']= calls
            session.save()
            permanent_list = []
            for call in calls:
                temp_list  = []
                temp_list.append((call.date_time_called.strftime("%m/%d/%Y - %H:%M")))
                temp_list.append(call.emergencyDescription)
                temp_list.append(call.municipality)
                temp_list.append(call.extendedLocationInfo)
                temp_list.append(call.status)
                temp_list.append(call.callId)
                permanent_list.append(temp_list)
            dbsession.close()
            return dict(page='providerHome', civilian_name=name, error_message =error_message, calls=permanent_list, user_email=email, municipalityList = municipalities)
        elif location or municipality or description or urgency:
            error_message = "Fill out all fields. Try again!"
        permanent_list = []
        for call in calls:
            temp_list  = []
            temp_list.append((call.date_time_called.strftime("%m/%d/%Y - %H:%M")))
            temp_list.append(call.emergencyDescription)
            temp_list.append(call.municipality)
            temp_list.append(call.extendedLocationInfo)
            temp_list.append(call.status)
            temp_list.append(call.callId)
            permanent_list.append(temp_list)
        return dict(page='providerHome',civilian_name = name, error_message =error_message, calls=permanent_list , user_email=email, municipalityList = municipalities)

    @expose("pages/providerSignUpPage.xhtml")
    def providerSignup(self, name=None, orgEmail=None, orgID=None, password=None, confirmPassword=None, orgName= None):
        error_message = ''
        check = 0
        if name and orgEmail and orgID and orgName and password == confirmPassword:
            try:
                new_user = User(email=orgEmail, name=name, password=password, orgName=orgName)
                Session = sessionmaker(bind=engine)
                dbsession = Session()
                organization = dbsession.query(Orgs).filter_by(orgName=orgName).first()
                if not organization:
                    raise ValueError
                check += 1
                if int(orgID) == int(organization.orgPin):
                    check +=1
                    dbsession.add(new_user)
                    dbsession.commit()
                    session['name'] = new_user.name
                    session['email'] = new_user.email
                    session['orgName'] = orgName
                    session['calls'] = []
                    session['municipality'] = "Adjuntas"
                    session.save()
                    dbsession.close()
                    # Optionally, you can redirect to a success page
                    return redirect("/providerHomePage")
                else:
                    error_message = "Organization ID does not match your organization. Try again with a different ID!"
                    return dict(page='providerSignUpPage', error_message=error_message)
            except (ValueError, IntegrityError):
                if check == 0:
                    error_message = "That organization is not in our records. Try again with a different organization name."
                elif check == 1:
                    error_message = "The organization ID is a numberical value"
                else:
                    error_message = "Email is already in use. Please choose a different email."
                return dict(page='providerSignUpPage', error_message=error_message)
        else:
            if (password != confirmPassword):
                error_message = 'Passwords do not match. Try again!'
            elif(name or orgEmail or password or confirmPassword):
                error_message = "Fill out all fields. Try again!"
            return dict(page='providerSignUpPage', error_message=error_message)
        
    @expose("pages/hubPage.xhtml")
    def hubPage(self, municipality=None, zipcode=None, city=None, streetAddr=None, aidDescription=None, currCapacity=None, delete_button=None):
        error_message = ''
        Session = sessionmaker(bind=engine)
        dbsession = Session()
        aidDisplay = ''
        cap = ''

        checkHub = dbsession.query(Hubs).filter_by(mainProvider=session['email']).first()
        if checkHub is not None:
            cap = ''
            if checkHub.currCapacity == 1:
                cap = 'Under Capacity'
            elif checkHub.currCapacity == 2:
                cap = 'Max Capacity'
            else:
                cap = 'Over Capacity'
            aidDisplay = "\nAddress:\n" + checkHub.streetAddr + ", " + checkHub.city + " " + checkHub.zipcode + ", " + checkHub.municipality + "\n\nProvisions:\n" + checkHub.aidDescription + "\n\nCurrent Capacity:\n" + cap
        else:
            aidDisplay = "If you're the leader of resource hub, put it on your profile for citizens and other aid providers to see."

        if municipality and zipcode and city and streetAddr and aidDescription and currCapacity:
            checkHub = dbsession.query(Hubs).filter_by(mainProvider=session['email']).first()
            if checkHub is not None:
                checkHub.municipality=municipality
                checkHub.zipcode=zipcode
                checkHub.city=city
                checkHub.streetAddr=streetAddr
                checkHub.aidDescription=aidDescription
                checkHub.currCapacity=currCapacity
            else:
                newHub = Hubs(mainProvider=session['email'], municipality=municipality, zipcode=zipcode, city=city, streetAddr=streetAddr, aidDescription=aidDescription, currCapacity=currCapacity)
                dbsession.add(newHub)
            dbsession.commit()
            dbsession.close()
            now = datetime.now()
            date_time = now.strftime("%m/%d/%Y - %H:%M")
            error_message = 'Hub successfully updated: ' + date_time
            cap = ''
            if currCapacity == 1:
                cap = 'Under Capacity'
            elif currCapacity == 2:
                cap = 'Max Capacity'
            else:
                cap = 'Over Capacity'
            aidDisplay = "\nAddress:\n" + streetAddr + ", " + city + " " + zipcode + ", " + municipality + "\n\nProvisions:\n" + aidDescription + "\n\nCurrent Capacity:\n" + cap
            return dict(page='hubPage', civilian_name = session['name'], error_message = error_message, aidDisplay=aidDisplay, municipalityList = municipalities)
        elif municipality or zipcode or city or streetAddr or aidDescription or currCapacity:
            error_message = "You must fill out all hub fields."
            return dict(page='hubPage', civilian_name = session['name'], error_message=error_message, aidDisplay=aidDisplay, municipalityList = municipalities)
        elif delete_button == "Delete Your Hub":
            checkHub = dbsession.query(Hubs).filter_by(mainProvider=session['email']).first()
            if checkHub is not None:
                dbsession.delete(checkHub)
                dbsession.commit()
                now = datetime.now()
                date_time = now.strftime("%m/%d/%Y - %H:%M")
                error_message = 'Hub successfully deleted: ' + date_time
                aidDisplay = "If you're the leader of resource hub, put it on your profile for citizens and other aid providers to see."
            else:
                error_message = 'No hub to delete'
            dbsession.close()
        return dict(page='hubPage', civilian_name = session['name'], error_message=error_message, aidDisplay=aidDisplay, municipalityList = municipalities)

    @expose("pages/login.xhtml")
    def logIn(self, email=None, password=None):
        error_message = ''
        if email and password:
            try:
                Session = sessionmaker(bind=engine)
                dbsession = Session()
                currUser = dbsession.query(User).filter_by(email=email).first()
                if currUser.password != password:
                    error_message = "Wrong password for email. Try again!"
                    return dict(page='login', error_message=error_message)
                session['name'] = currUser.name
                session['email'] = currUser.email
                session['calls'] = currUser.children
                if currUser.orgName != "None":
                    session['orgName'] = currUser.orgName
                    session['municipality'] = "Adjuntas"
                    dbsession.close()
                    session.save()
                    return redirect("/providerHomePage")
                else:
                    dbsession.close()
                    session.save()
                    return redirect("/citizenHomePage")
            except AttributeError as a:
                error_message = "No User associated to your email."
        elif email or password:
            error_message = "Fill out all fields. Try again!"
        return dict(page='login', error_message=error_message)
    

    @expose("pages/municipalityCallsPage.xhtml")
    def municipalityCalls(self, municipality_name):
        Session = sessionmaker(bind=engine)
        dbsession = Session()
        curMun = dbsession.query(MunicipalityUrgency).filter_by(municipality=municipality_name).first()
        calls = dbsession.query(EmergencyCall).filter_by(municipality=municipality_name).all()
        municipalitychatlist = dbsession.query(MunicipalityChats).where(MunicipalityChats.municipality == municipality_name).order_by(MunicipalityChats.date_time.desc())
        citList = []
        proList = []
        for call in calls:
            curUser = dbsession.query(User).filter_by(email=call.user_email).first()
            userType = "citizen" if curUser.orgName == 'None' else "provider"
            if userType == 'citizen':
                temp_list  = []
                temp_list.append(curUser.email)
                temp_list.append((call.date_time_called.strftime("%m/%d/%Y - %H:%M")))
                temp_list.append(call.emergencyDescription)
                temp_list.append(call.extendedLocationInfo)
                temp_list.append(call.status)
                temp_list.append(call.callId)
                citList.append(temp_list)
            else:
                temp_list  = []
                temp_list.append(curUser.email)
                temp_list.append(curUser.orgName)
                temp_list.append((call.date_time_called.strftime("%m/%d/%Y - %H:%M")))
                temp_list.append(call.emergencyDescription)
                temp_list.append(call.extendedLocationInfo)
                temp_list.append(call.status)
                temp_list.append(call.callId)
                proList.append(temp_list)
        citCount = len(citList)
        proCount = len(proList)
        hubs = dbsession.query(Hubs).filter_by(municipality=municipality_name).all()
        hubList = []
        for hub in hubs:
            curUser = dbsession.query(User).filter_by(email=hub.mainProvider).first()
            if hub.currCapacity == 1:
                cap= "Under Capacity"
            elif hub.currCapacity == 2:
                cap= "Maximum Capacity"
            else:
                cap = "Over Capacity"
            temp_list  = []
            temp_list.append(curUser.orgName)
            temp_list.append(hub.municipality)
            temp_list.append(hub.zipcode)
            temp_list.append(hub.streetAddr)
            temp_list.append(hub.aidDescription)
            temp_list.append(cap)
            hubList.append(temp_list)
        dbsession.close()
        if municipality_name in municipalities:
            return dict(page='municipalityCallsPage', municipality_name=municipality_name, citCalls=citList, proCalls=proList, urgency_Rating=curMun.urgency_rating, hubList = hubList, municipalitychats=municipalitychatlist, user_email = session['email'], proCount = proCount, citCount= citCount)
        else:
            response.status_code = 404
            return 'Invalid municipality name.'
    
    @expose("pages/municipalityHubsPage.xhtml")
    def municipalityHubs(self, municipality_name):
        Session = sessionmaker(bind=engine)
        dbsession = Session()
        curMun = dbsession.query(MunicipalityUrgency).filter_by(municipality=municipality_name).first()
        hubs = dbsession.query(Hubs).filter_by(municipality=municipality_name).all()
        hubList = []
        for hub in hubs:
            curUser = dbsession.query(User).filter_by(email=hub.mainProvider).first()
            if hub.currCapacity == 1:
                cap= "Under Capacity"
            elif hub.currCapacity == 2:
                cap= "Maximum Capacity"
            else:
                cap = "Over Capacity"
            temp_list  = []
            temp_list.append(curUser.orgName)
            temp_list.append(hub.municipality)
            temp_list.append(hub.zipcode)
            temp_list.append(hub.streetAddr)
            temp_list.append(hub.aidDescription)
            temp_list.append(cap)
            hubList.append(temp_list)

        dbsession.close()
        if municipality_name in municipalities:
            return dict(page='municipalityHubsPage', municipality_name=municipality_name, hubList=hubList, urgency_Rating=curMun.urgency_rating)
        else:
            response.status_code = 404
            return 'Invalid municipality name.'
    
    @expose('json')
    def search(self, searchTerm):
        if searchTerm in municipalities:
            Session = sessionmaker(bind=engine)
            dbsession = Session()
            isCitizen = dbsession.query(User.orgName).filter_by(email=session['email']).first() == 'None'
            if isCitizen:
                redirect_url = '/municipalityHubs/{}'.format(searchTerm)

            else:
                redirect_url = '/municipalityCalls/{}'.format(searchTerm)
            return {'valid': True, 'redirect_url': redirect_url}
        else:
            response.status_code = 404
            return {'error': 'Invalid search term.'}
        
    
    @expose("pages/vulnerabilityMap.xhtml")
    def vulnerabilityMap(self):
        Session = sessionmaker(bind=engine)
        dbsession = Session()

        zip_codes = dbsession.query(Hubs.zipcode).all()
        curUser = dbsession.query(User.orgName).filter_by(email=session['email']).first()
        isCitizen = curUser.orgName == 'None'
        zip_codes_list = []
        for zip in zip_codes: 
            zip_codes_list.append(zip[0])
        zip_codes_json = json.dumps(zip_codes_list)

        aid_hubs = dbsession.query(Hubs.mainProvider, Hubs.municipality, Hubs.zipcode, Hubs.city, Hubs.streetAddr, Hubs.aidDescription, Hubs.currCapacity).all() 
        aid_hubs_list = []
        for mainProvider, muncipality, zipcode, city, streetAddr, aidDescription, currCapacity in aid_hubs: 
            aid_hubs_list.append([mainProvider, muncipality, zipcode, city, streetAddr, aidDescription, currCapacity])
        aid_hubs_json = json.dumps(aid_hubs_list)

        urgency_ratings = dbsession.query(MunicipalityUrgency.municipality, MunicipalityUrgency.urgency_rating,).all()
        urgency_ratings_list = []
        for muncipality, rating in urgency_ratings: 
            urgency_ratings_list.append([muncipality, rating])
        
        urgency_ratings_json = json.dumps(urgency_ratings_list)

        return dict(page='testingMap', zip_codes=zip_codes_json, isCitizen = isCitizen, urgency_ratings=urgency_ratings_json, aid_hubs = aid_hubs_json, municipalityList = municipalities)
    

    
    @expose('json')
    def get_geojson(self):
        
            # Replace 'path/to/your/myjson.json' with the actual path to your GeoJSON file
        with open('myjson.json', 'r') as geojson_file:
            geojson_data = json.load(geojson_file)
            
        # Set appropriate headers for the JSON response
        response.content_type = 'application/json'
        
        return geojson_data

    @expose("pages/callRespondPage.xhtml")
    def callRespondPage(self, callId, urgency=None, resolution=None, description=None, location=None,messageToCaller=None,damages=None, resources=None, colab=None):
        error_message = ''
        if urgency and resolution and description and location and messageToCaller:
            now = datetime.now()
            newResponse = EmergencyCallsResponses(
                callId=callId,
                date_time_responded = now,
                urgency=urgency,
                resolution=resolution,
                emergencyDescription=description,
                location=location,
                messageToCaller=messageToCaller,
                damages=damages if damages is not None else "None",
                resources=resources if resources is not None else "None",
                colabOrg=colab if colab is not None else "None"
            )
            Session = sessionmaker(bind=engine)
            dbsession = Session()
            dbsession.add(newResponse)
            dbsession.commit()
            emerCall = dbsession.query(EmergencyCall).filter_by(callId=callId).first()
            old_stat = 0
            new_stat = 0
            if emerCall.status == "Arrived":
                old_stat += 1/4
            elif emerCall.status == "Seen":
                old_stat += 2/4
            elif emerCall.status == "Not seen":
                old_stat += 3/4
            elif emerCall.status == "NeedHelp":
                old_stat += 3/4
            elif emerCall.status == 'NeedCriticalHelp':
                old_stat += 1
            if resolution == "Arrived":
                new_stat += 1/4
            elif resolution == "Seen":
                new_stat += 2/4
            elif resolution == "Not seen":
                new_stat += 3/4
            elif resolution == "NeedHelp":
                new_stat += 3/4
            elif resolution == 'NeedCriticalHelp':
                new_stat += 1
            emerCall.status = resolution
            municipality = emerCall.municipality
            curMun = dbsession.query(MunicipalityUrgency).filter_by(municipality=municipality).first()
            curMun.urgency_rating += + (new_stat*stat_weight) - (old_stat*stat_weight)
            dbsession.commit()
            curMun.urgency_rating += (int(urgency)*urg_weight)/4 - (emerCall.urgency*urg_weight)/4
            emerCall.urgency = urgency
            dbsession.commit()
            callUser = dbsession.query(User).filter_by(email=emerCall.user_email).first()
            session['calls']=callUser.children
            session.save()
            permanent_list = []
            callResponses = emerCall.responses
            urg = ''
            if urgency == "1":
                urg = 'Minor'
            elif urgency == "2":
                urg = 'Major'
            elif urgency == "0":
                urg = 'None'
            elif urgency == "3":
                urg = 'Major'
            elif urgency == "4":
                urg = 'Critical'
            for resp in callResponses:
                temp_list  = []
                temp_list.append((resp.date_time_responded.strftime("%m/%d/%Y - %H:%M")))
                temp_list.append((now - emerCall.date_time_called).days)
                temp_list.append(resp.emergencyDescription)
                temp_list.append(resp.location)
                temp_list.append(resp.damages)
                temp_list.append(resp.resources)
                temp_list.append(resp.colabOrg)
                temp_list.append(resp.resolution)
                permanent_list.append(temp_list)
            dbsession.close()
            return dict(page='callRespondPage', callId=callId, error_message=error_message, responses=permanent_list, emergencyCall=emerCall, urg = urg)
        elif urgency or resolution or description or location:
            error_message = "Enter all required fields"

        Session = sessionmaker(bind=engine)
        dbsession = Session()
        emerCall = dbsession.query(EmergencyCall).filter_by(callId=callId).first()
        urg = ''
        if emerCall.urgency == 1:
            urg = 'Minor'
        elif emerCall.urgency == 2:
            urg = 'Major'
        elif emerCall.urgency == 0:
            urg = 'None'
        elif emerCall.urgency == 3:
            urg = 'Major'
        elif emerCall.urgency == 4:
            urg = 'Critical'
        permanent_list = []
        callResponses = emerCall.responses
        for resp in callResponses:
            temp_list  = []
            temp_list.append((resp.date_time_responded.strftime("%m/%d/%Y - %H:%M")))
            temp_list.append((resp.date_time_responded - emerCall.date_time_called).days)
            temp_list.append(resp.emergencyDescription)
            temp_list.append(resp.location)
            temp_list.append(resp.damages)
            temp_list.append(resp.resources)
            temp_list.append(resp.colabOrg)
            temp_list.append(resp.resolution)
            permanent_list.append(temp_list)
        dbsession.close()
        return dict(page='callRespondPage', callId=callId, error_message=error_message, responses=permanent_list, emergencyCall=emerCall, urg=urg)
    
    @expose("pages/citCallResponsesPage.xhtml")
    def citCallResponsesPage(self, callId, urgency=None, description=None, resolution=None, location=None):
        Session = sessionmaker(bind=engine)
        dbsession = Session()
        callUser = dbsession.query(User).filter_by(email=session['email']).first()
        emerCall = dbsession.query(EmergencyCall).filter_by(callId=callId).first()
        isCitizen = callUser.orgName == "None"
        if urgency or resolution or description or location:
            now = datetime.now()
            emerCall.lastUpdated = now
            municipality = emerCall.municipality
            curMun = dbsession.query(MunicipalityUrgency).filter_by(municipality=municipality).first()
            old_stat = 0
            new_stat = 0
            if emerCall.status == "Arrived":
                old_stat += 1/4
            elif emerCall.status == "Seen":
                old_stat += 2/4
            elif emerCall.status == "Not seen":
                old_stat += 3/4
            elif emerCall.status == "NeedHelp":
                old_stat += 3/4
            elif emerCall.status == 'NeedCriticalHelp':
                old_stat += 1
            if resolution == "Arrived":
                new_stat += 1/4
            elif resolution == "Seen":
                new_stat += 2/4
            elif resolution == "Not seen":
                new_stat += 3/4
            elif resolution == "NeedHelp":
                new_stat += 3/4
            elif resolution == 'NeedCriticalHelp':
                new_stat += 1
            if urgency:
                curMun.urgency_rating = curMun.urgency_rating + (urg_weight*int(urgency))/4 - (urg_weight*int(emerCall.urgency))/4
                emerCall.urgency=urgency
                dbsession.commit()
            if location:
                emerCall.extendedLocationInfo = location
            if description:
                emerCall.emergencyDescription = description
            if resolution == 'Resolved':
                curMun.urgency_rating -= (stat_weight*old_stat) + (urg_weight*int(emerCall.urgency))/4 + (1/max_calls)*(num_call_weight)
                dbsession.commit()
                for resp in emerCall.responses:
                    dbsession.delete(resp)
                dbsession.delete(emerCall)
                dbsession.commit()
                session['calls']=callUser.children
                session.save()
                dbsession.close()
                if callUser.orgName == 'None':
                    return redirect("/citizenHomePage")
                return redirect("/providerHomePage")
            elif resolution:
                curMun.urgency_rating = curMun.urgency_rating + (stat_weight*new_stat) - (stat_weight*old_stat)
                dbsession.commit()
                emerCall.status = resolution
            dbsession.commit()
            permanent_list = []
            callResponses = emerCall.responses
            session['calls']=callUser.children
            session.save()
            for resp in callResponses:
                temp_list  = []
                temp_list.append((resp.date_time_responded.strftime("%m/%d/%Y - %H:%M")))
                temp_list.append((now - emerCall.date_time_called).days)
                temp_list.append(resp.emergencyDescription)
                temp_list.append(resp.location)
                temp_list.append(resp.damages)
                temp_list.append(resp.resources)
                temp_list.append(resp.colabOrg)
                temp_list.append(resp.resolution)
                permanent_list.append(temp_list)
            dbsession.close()
            return dict(page='citCallResponsePage', callId=callId, responses=permanent_list, emergencyCall=emerCall, isCitizen=isCitizen)
        permanent_list = []
        callResponses = emerCall.responses
        for resp in callResponses:
            temp_list  = []
            temp_list.append((resp.date_time_responded.strftime("%m/%d/%Y - %H:%M")))
            temp_list.append((resp.date_time_responded - emerCall.date_time_called).days)
            temp_list.append(resp.emergencyDescription)
            temp_list.append(resp.location)
            temp_list.append(resp.damages)
            temp_list.append(resp.resources)
            temp_list.append(resp.colabOrg)
            temp_list.append(resp.resolution)
            permanent_list.append(temp_list)
        dbsession.close()
        return dict(page='citCallResponsePage', callId=callId, responses=permanent_list, emergencyCall=emerCall,isCitizen=isCitizen)
    
    @expose("pages/chatPage.xhtml")
    def chatPage(self, chatSubmit=None, send=None, municipalitySubmit=None, msend =None, minput=None):
        name = session['name']
        email = session['email']
        municipalityList=municipalities

        Session = sessionmaker(bind=engine)
        dbsession = Session()
        chats = dbsession.query(Chats).order_by(Chats.date_time.desc())
        chatlist = chats
        municipality = session['municipality']
        municipalitychatlist = dbsession.query(MunicipalityChats).where(MunicipalityChats.municipality == municipality).order_by(MunicipalityChats.date_time.desc())
        dbsession.expunge_all()
        error_message = ''
        if chatSubmit and send:
            Session = sessionmaker(bind=engine)
            dbsession = Session()
            now = datetime.now()
            new_chat = Chats(chat=chatSubmit, user_email = email, date_time = now)
            dbsession.add(new_chat)
            dbsession.commit()
        
        if municipalitySubmit and msend:
            Session = sessionmaker(bind=engine)
            dbsession = Session()
            now = datetime.now()            
            new_chat = MunicipalityChats(chat=municipalitySubmit, user_email = email, date_time=now, municipality=municipality)
            dbsession.add(new_chat)
            dbsession.commit()
            municipality = session['municipality']
            municipalitychatlist = dbsession.query(MunicipalityChats).where(MunicipalityChats.municipality == municipality).order_by(MunicipalityChats.date_time.desc())
            return dict(page='chatPage', provider_name=name, error_message=error_message, chats=chatlist, user_email=email, municipality=municipality, municipalities=municipalityList, municipalitychats=municipalitychatlist)


        if msend and minput:
            session['municipality'] = minput
            session.save()
            municipality = minput
            municipalitychatlist = dbsession.query(MunicipalityChats).where(MunicipalityChats.municipality == municipality).order_by(MunicipalityChats.date_time.desc())
            return dict(page='chatPage', provider_name=name, error_message=error_message, chats=chatlist, user_email=email, municipality=municipality, municipalities=municipalityList, municipalitychats=municipalitychatlist)


        
        return dict(page='chatPage', provider_name=name, error_message=error_message, chats=chatlist, user_email=email, municipality=municipality, municipalities=municipalityList, municipalitychats=municipalitychatlist)
    @expose()
    def chatSubmit(self, municipalityName, municipalitySubmit=None, msend =None):
        if municipalitySubmit and msend:
            Session = sessionmaker(bind=engine)
            dbsession = Session()
            now = datetime.now()            
            new_chat = MunicipalityChats(chat=municipalitySubmit, user_email = session['email'], date_time=now, municipality=municipalityName)
            dbsession.add(new_chat)
            dbsession.commit()
            return redirect("/municipalityCalls/"+municipalityName)


