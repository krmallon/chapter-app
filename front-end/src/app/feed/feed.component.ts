import { Component, OnInit } from '@angular/core';
import { FeedService } from '../services/feed.service';

@Component({
  selector: 'app-feed',
  templateUrl: './feed.component.html',
  styleUrls: ['./feed.component.scss']
})
export class FeedComponent implements OnInit {

  public sessionStorage = sessionStorage;
  
  constructor(public feedService: FeedService) { }

  ngOnInit(): void {
    this.feedService.getFollowedActivity(sessionStorage.user_id)
  }

  actionType(activity) {
    return activity.action
  }
  
  objectType(activity) {
    return activity.object_id
  }
}
