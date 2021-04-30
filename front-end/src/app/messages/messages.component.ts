import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { MessagingService } from '../services/messaging.service';
import { NotificationService } from '../services/notification.service';
import { SearchService } from '../services/search.service';

@Component({
  selector: 'app-messages',
  templateUrl: './messages.component.html',
  styleUrls: ['./messages.component.scss']
})
export class MessagesComponent implements OnInit {

  newMessageForm;
  userSearchForm;
  partner;

  constructor(public messagingService: MessagingService, public notifyService: NotificationService, private formBuilder : FormBuilder, private route: ActivatedRoute, public searchService: SearchService) { }

  ngOnInit(): void {

    this.newMessageForm = this.formBuilder.group({
      message: ['', Validators.required]
    });

    this.userSearchForm = this.formBuilder.group({
      query: ['', Validators.required]
    })

    this.messagingService.getReceivedMessages(sessionStorage.user_id)
    this.messagingService.getChatPartners(sessionStorage.user_id)
    if (this.chatOpen()) {
      this.messagingService.getConversation(sessionStorage.user_id, this.route.snapshot.params.user_id)
    }
  }
  
  setPartner(partner) {
    this.partner = partner.id;
    console.log(this.partner)
  }
  
  loadChat(partner_id) {
    console.log("loading chat with " + partner_id)
    this.messagingService.getConversation(sessionStorage.user_id, partner_id)
  }
  
  sentMessage(msg) {
    return msg.sender == sessionStorage.user_id
  }
  
  receivedMessage(msg) {
    return msg.recipient == sessionStorage.user_id
  }
  
  onSend() {
    console.log(this.newMessageForm.value)
    this.messagingService.sendMessage(sessionStorage.user_id, this.route.snapshot.params.user_id, this.newMessageForm.value)
    this.newMessageForm.reset()
    this.loadChat(this.route.snapshot.params.user_id)
    this.messagingService.getChatPartners(sessionStorage.user_id)
    this.notifyService.showSuccess('Message sent', 'Success')
    
    // this.webService.getChatPartners(sessionStorage.user_id)
    // console.log(this.route.snapshot.params.user_id)
  }
  
  chatOpen() {
    return this.route.snapshot.params.user_id
  }

  userSelected(id) {
    return this.route.snapshot.params.user_id == id
  }

  setChatAsActive() {
  }
  

  

}
