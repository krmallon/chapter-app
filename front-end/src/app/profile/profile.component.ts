import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { GoalService } from '../services/goal.service';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {

  constructor(public goalService: GoalService, private route: ActivatedRoute) { }

  ngOnInit(): void {
    this.goalService.getGoal(this.route.snapshot.params.id)
  }

  getGoalCompletion(current, target) {
    return (current / target) * 100
  }
}
