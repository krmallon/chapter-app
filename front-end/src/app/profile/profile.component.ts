import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from '../auth.service';
import { AchievementService } from '../services/achievement.service';
import { BookService } from '../services/book.service';
import { GoalService } from '../services/goal.service';
import { NotificationService } from '../services/notification.service';
import { ReviewService } from '../services/review.service';
import { StatService } from '../services/stat.service';
import { UserService } from '../services/user.service';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {

  public sessionStorage = sessionStorage
  // coverImage;
  editProfileForm;

  constructor(public authService: AuthService, public statService: StatService, public notifyService: NotificationService, public goalService: GoalService, public userService: UserService, public bookService: BookService, public reviewService: ReviewService, public achievementService: AchievementService, private route: ActivatedRoute,
    private formBuilder: FormBuilder) { }

  ngOnInit(): void {
    this.userService.getProfileDetails(this.route.snapshot.params.id)
    // this.reviewService.getReviewsByUser(this.route.snapshot.params.id)
    this.goalService.getGoal(this.route.snapshot.params.id)
    this.userService.checkFollowing(this.route.snapshot.params.id, sessionStorage.user_id)
    this.bookService.getCurrentlyReadingByUser(this.route.snapshot.params.id)
    this.bookService.getWantsToReadByUser(this.route.snapshot.params.id)
    this.bookService.getHasReadByUser(this.route.snapshot.params.id)
    this.achievementService.getUserAchievements(this.route.snapshot.params.id)
    this.statService.getMostRead(this.route.snapshot.params.id)
    this.statService.getTotalPagesRead(this.route.snapshot.params.id)

    this.editProfileForm = this.formBuilder.group({
      name: ['', Validators.maxLength(50)],
      image: ['', Validators.pattern('^.+png$')]
    });
  }

  getGoalCompletion(current, target) {
    return (current / target) * 100
  }

  isOwnProfile() {
    return this.route.snapshot.params.id == sessionStorage.user_id;
  }

  following() {
    return this.userService.following
  }

  onFollow() {
    this.userService.followUser(this.route.snapshot.params.id, sessionStorage.user_id)
    this.notifyService.showSuccess('Followed user', 'Success')
  }

  onUnfollow() {
    this.userService.unfollowUser(this.route.snapshot.params.id, sessionStorage.user_id)
    this.notifyService.showSuccess('Unfollowed user', 'Success')
  }

  isInvalid(control) {
    return this.editProfileForm.controls[control].invalid &&
           this.editProfileForm.controls[control].touched;
  }

  isUnTouched() {
    return this.editProfileForm.controls.name.pristine && this.editProfileForm.controls.image.pristine
  }

  isIncomplete() {
    return this.isInvalid('name') || this.isInvalid('image') || this.isUnTouched();
  }

}
