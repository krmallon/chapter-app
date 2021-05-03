import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import axios from 'axios';
import { Subject } from 'rxjs';
import config from '../config';

@Injectable({
  providedIn: 'root'
})
export class GoalService {

  private goal_private_list;
  private goalSubject = new Subject();
  goal_list = this.goalSubject.asObservable();

  percentageComplete;
  currentYear = "2021";
  // goalOptions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

  constructor(private http: HttpClient) { }


  getGoal(user_id) {
    return this.http.get(config.app_url + user_id + '/goals')
    .subscribe(response => { 
        this.goal_private_list = response;
        this.goalSubject.next(this.goal_private_list);
    });
    
  }

  setGoal(goal) {
    let goalData = new FormData();
    goalData.append("user_id", sessionStorage.user_id)
    goalData.append("target", goal.goalFormControl)
    goalData.append("year", this.currentYear)

    axios.post(config.app_url + 'goals/new', goalData)
  }

  editGoal(goal) {
    let goalData = new FormData()
    goalData.append("target", goal.goalFormControl)
    
    axios.put(config.app_url + 'goals/' + goal.id, goalData)
  }
}
