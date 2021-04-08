import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from '../auth.service';
import { AchievementService } from '../services/achievement.service';
import { BookService } from '../services/book.service';
import { GoalService } from '../services/goal.service';
import { ReviewService } from '../services/review.service';
import { StatService } from '../services/stat.service';
import { UserService } from '../services/user.service';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {

  constructor(public authService: AuthService, public statService: StatService, public goalService: GoalService, public userService: UserService, public bookService: BookService, public reviewService: ReviewService, public achievementService: AchievementService, private route: ActivatedRoute) { }

  ngOnInit(): void {
    this.userService.getProfileDetails(this.route.snapshot.params.id)
    this.reviewService.getReviewsByUser(this.route.snapshot.params.id)
    this.goalService.getGoal(this.route.snapshot.params.id)
    this.userService.checkFollowing(this.route.snapshot.params.id, sessionStorage.user_id)
    this.bookService.getCurrentlyReadingByUser(this.route.snapshot.params.id)
    this.achievementService.getUserAchievements(this.route.snapshot.params.id)
    this.statService.getMostRead(this.route.snapshot.params.id)
    this.statService.getTotalPagesRead(this.route.snapshot.params.id)
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

  follow() {
    this.userService.followUser(this.route.snapshot.params.id, sessionStorage.user_id)
  }

  unfollow() {
    this.userService.unfollowUser(this.route.snapshot.params.id, sessionStorage.user_id)
  }

}
