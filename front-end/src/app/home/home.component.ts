import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { AuthService } from '../auth.service';
import { FeedService } from '../services/feed.service';
import { GoalService } from '../services/goal.service';
import { UserService } from '../services/user.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {

  goalForm;

  public sessionStorage = sessionStorage;

  constructor(public feedService: FeedService, public authService: AuthService, public userService: UserService, private formBuilder: FormBuilder, public goalService: GoalService) { }

  ngOnInit(): void {
    // this.userService.getCurrentUser(sessionStorage.getItem("user"))
    this.feedService.getFollowedActivity(sessionStorage.user_id)
    this.userService.getProfileDetails(sessionStorage.user_id)

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
}
