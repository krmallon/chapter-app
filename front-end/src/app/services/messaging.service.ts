import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MessagingService {

  private rec_messages_private_list;
  private recMessagesSubject = new Subject();
  rec_messages_list = this.recMessagesSubject.asObservable();

  private convo_messages_private_list;
  private convoMessagesSubject = new Subject();
  convo_messages_list = this.convoMessagesSubject.asObservable();

  private msg_partners_private_list;
  private msgPartnersSubject = new Subject()
  msg_partners_list = this.msgPartnersSubject.asObservable();

  constructor(private http: HttpClient) { }

  getReceivedMessages(user_id) {
    return this.http.get('http://localhost:5000/api/v1.0/user/' + user_id + '/messages/received').subscribe(
        response => {
            this.rec_messages_private_list = response;
            this.recMessagesSubject.next(this.rec_messages_private_list);
        }
    )
}

getConversation(user_id, partner_id) {
    return this.http.get('http://localhost:5000/api/v1.0/messages/?userA=' + user_id + '&userB=' + partner_id).subscribe(
        response => {
            this.convo_messages_private_list = response;
            this.convoMessagesSubject.next(this.convo_messages_private_list);
        }
    )
}

getChatPartners(user_id) {
  return this.http.get('http://localhost:5000/api/v1.0/user/' + user_id + '/messages/participants').subscribe(
      response => {
          this.msg_partners_private_list = response;
          this.msgPartnersSubject.next(this.msg_partners_private_list);
      }
  )
  
}

sendMessage(sender_id, recipient_id, message) {
  let postData = new FormData();

  // append user ID and user nickname from Auth0 profile object
  // postData.append("id", "10");
  postData.append("sender_id", sender_id);
  postData.append("recipient_id", recipient_id);
  postData.append("msg_text", message.message);
  // postData.append("rating", review.rating);

  this.http.post(
      'http://localhost:5000/api/v1.0/user/' + recipient_id + '/contact',
      postData).subscribe(
      response => {
      // this.getBookID(isbn)
      // this.getReviews(isbn);
      } );
}


}
