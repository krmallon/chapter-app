import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import config from '../config';

@Injectable({
  providedIn: 'root'
})
export class MessagingService {

  unread;

  private rec_messages_private_list;
  private recMessagesSubject = new Subject();
  rec_messages_list = this.recMessagesSubject.asObservable();

  private convo_messages_private_list;
  private convoMessagesSubject = new Subject();
  convo_messages_list = this.convoMessagesSubject.asObservable();

  private msg_partners_private_list;
  private msgPartnersSubject = new Subject()
  msg_partners_list = this.msgPartnersSubject.asObservable();

  private unread_private_count;
  private unreadCountSubject = new Subject()
  unread_count = this.unreadCountSubject.asObservable();

  constructor(private http: HttpClient) { }

  getReceivedMessages(user_id) {
    return this.http.get(config.app_url + 'user/' + user_id + '/messages/received').subscribe(
        response => {
            this.rec_messages_private_list = response;
            this.recMessagesSubject.next(this.rec_messages_private_list);
        }
    )
}

getConversation(user_id, partner_id) {
    return this.http.get(config.app_url + 'messages/?userA=' + user_id + '&userB=' + partner_id).subscribe(
        response => {
            this.convo_messages_private_list = response;
            this.convoMessagesSubject.next(this.convo_messages_private_list);
        }
    )
}

getChatPartners(user_id) {
  return this.http.get(config.app_url + 'user/' + user_id + '/messages/participants').subscribe(
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
      config.app_url + 'user/' + recipient_id + '/contact',
      postData).subscribe(
      response => {
      // this.getBookID(isbn)
      // this.getReviews(isbn);
      } );
}

getUnreadCount(user_id) {
    this.http.get(config.app_url + 'user/' + user_id + '/messages/unread').subscribe(
        response => {
            this.unread_private_count = response;
            console.log(response)
            this.unreadCountSubject.next(this.unread_private_count)
        }
    )
}


}
