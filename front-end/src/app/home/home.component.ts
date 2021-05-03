import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { AuthService } from '../auth.service';
import { AchievementService } from '../services/achievement.service';
import { FeedService } from '../services/feed.service';
import { GoalService } from '../services/goal.service';
import { LikeService } from '../services/like.service';
import { MessagingService } from '../services/messaging.service';
import { NotificationService } from '../services/notification.service';
import { UserService } from '../services/user.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  goalOptions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
  goalForm;
  feedObjectID = 7

  // unreadCount;

  public sessionStorage = sessionStorage;

  constructor(public feedService: FeedService, public notifyService: NotificationService, public authService: AuthService, public achievementService: AchievementService, public messagingService: MessagingService, public likeService: LikeService, public userService: UserService, private formBuilder: FormBuilder, public goalService: GoalService) { }

  ngOnInit(): void {
    // this.userService.getCurrentUser(sessionStorage.getItem("user"))
    if (this.authService.loggedIn) {

      if (this.sessionStorage.getItem("user_id")=="N/A") {
        // let auth0_id = this.sessionStorage.getItem("user")
        this.userService.getCurrentUser(this.sessionStorage.getItem("user"))
        console.log("Setting user_id")
        this.ngOnInit()
      }

      // this.feedService.getFollowedActivity(sessionStorage.user_id)

      this.userService.getFollowedActivity(sessionStorage.user_id)
      this.userService.getProfileDetails(sessionStorage.user_id)
      this.userService.getFollowedUsers(sessionStorage.user_id)
      this.achievementService.getAllAchievements()

      

      // this.messagingService.getUnreadCount(sessionStorage.user_id)
      // this.unreadCount = this.messagingService.unread
      // console.log(this.unreadCount)

    }
    // this.feedService.getFollowedActivity(sessionStorage.user_id)
    // this.userService.getProfileDetails(sessionStorage.user_id)

    this.goalForm = this.formBuilder.group({
      goalFormControl: ['', Validators.required]
    });
  }

  // maybe move these methods to feedService
  actionType(activity) {
    return activity.action
  }

  objectType(activity) {
    return activity.object_id
  }

  likeUpdate(activity) {
    this.likeService.addLike(this.feedObjectID, activity.activity_id); 
    this.likeService.getLikes(this.feedObjectID, activity.activity_id)
  }

  refresh() {
    this.ngOnInit();
  }

  


}
