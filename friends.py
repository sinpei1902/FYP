import streamlit as st
import db

def preview():
    st.write("Add your friends here!")

def app():
    choice = st.selectbox("Select a task to manage:", ["Leaderboard", "Add Friends"])

    if choice == "Leaderboard":
        leaderboard()
    elif choice == "Add Friends":
        add_friends()

def leaderboard():
    friends = db.get_friends(st.session_state["username"])
    friends.append(st.session_state["username"]) #add user to leaderboard

    leaderboard_dict = []
    for user in friends:
        score = db.get_score(user)
        if user == st.session_state["username"]: 
            user = ""+user+" (you)" #change how user is displayed on leaderboard
        leaderboard_dict.append({"username": user, "score": score})

    #sort from highest to lowest score
    leaderboard_dict = sorted(leaderboard_dict, key=lambda x: x["score"], reverse=True)
    st.header("Leaderboard 🏆")
    rank = 0
    prev_score = None
    for i, entry in enumerate(leaderboard_dict, start=1):
        if entry["score"] != prev_score:
            rank = i
        prev_score = entry["score"]

        with st.container(border=True):
            col1, col2, col3 = st.columns([1,16,3])
            with col1:
                if rank==1:
                    st.header("🥇")
                elif rank==2:
                    st.header("🥈")
                elif rank==3:
                    st.header("🥉")
                else:
                    st.subheader(str(rank))
            with col2:
                st.subheader(entry['username'])
            with col3:
                st.subheader(str(entry['score'])+"🎖️")

    if len(friends)==1:
        st.subheader("Add friend to compete!")

def add_friends():
    #Send friend request
    st.subheader("Request a Friend")
    with st.form("Request a Friend"):
        requestee = st.text_input("Input friend's username: ")
        col1, col2 = st.columns([10,2])
        with col2:
            submitted = st.form_submit_button("Request")
            if submitted:
                with col1:
                    #check if requestee's username exists
                    if db.check_username_exists(requestee) == False:
                        st.error("Username does not exist")

                    #check if request has already been sent
                    elif db.check_if_requested(st.session_state["username"],requestee):
                        st.error("Request has already been sent")

                    #check if the requestee has already sent request to user
                    elif db.check_if_requested(requestee,st.session_state["username"]):
                        st.error("Your friend has already requested you. Please accept your friend's request.")

                    #check if already friends
                    elif db.check_if_friends(st.session_state["username"],requestee):
                        st.error("You are already friends with this user.")

                    #after all checks, send
                    else:
                        db.req_friend(st.session_state["username"],requestee)
                        st.success("Request Sent")

    #Accept friend reuqest 
    st.subheader("Requests Received:")
    requests = db.get_requests_received(st.session_state["username"])
    n = str(len(requests))
    with st.expander("Pending: "+n,expanded=True):
        st.write("")
        if requests:
            i=1 
            for request in requests:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([1,1,18])
                    with col1:
                        if st.button("☑️",key=str(i)+"☑️"):
                            db.accept_request(st.session_state["username"],request["requestor"])
                            st.rerun()
                    with col2:
                        if st.button("🗑️",key=str(i)+"🗑️"):
                            db.cancel_request(request["requestor"],st.session_state["username"])
                            st.rerun()
                    with col3:
                        st.write(f"{request["requestor"]}")
                    i+=1

        else: 
            st.write("No requests received and pending.")

    #Pending friend reuqests sent 
    st.subheader("Requests Sent:")
    requests = db.get_requests_sent(st.session_state["username"])
    n = str(len(requests))
    with st.expander("Pending: "+n,expanded=True):
        st.write("")
        if requests:
            i=1 
            for request in requests:
                with st.form(f"{i} sent"):
                    col1, col2 = st.columns([1,18])
                    i+=1
                    with col2:
                        st.write(f"{request["requestee"]}")
                    with col1:
                        submit = st.form_submit_button("🚫")
                if submit:
                    db.cancel_request(st.session_state["username"],request["requestee"])
                    st.rerun()
        else: 
            st.write("No requests sent and pending.")


