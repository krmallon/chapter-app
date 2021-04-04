import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { MessagingService } from '../services/messaging.service';

@Component({
  selector: 'app-messages',
  templateUrl: './messages.component.html',
  styleUrls: ['./messages.component.scss']
})
export class MessagesComponent implements OnInit {

  newMessageForm;
  partner;

  constructor(public messagingService: MessagingService, private formBuilder : FormBuilder, private route: ActivatedRoute) { }

  ngOnInit(): void {

    this.newMessageForm = this.formBuilder.group({
      message: ['', Validators.required]
    });

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
    // this.webService.getChatPartners(sessionStorage.user_id)
    // console.log(this.route.snapshot.params.user_id)
  }
  
  chatOpen() {
    return this.route.snapshot.params.user_id
  }

}
