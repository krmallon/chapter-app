import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import axios from 'axios';
import { Subject } from 'rxjs';

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
    return this.http.get('http://localhost:5000/api/v1.0/' + user_id + '/goals')
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

    axios.post('http://localhost:5000/api/v1.0/goals/new', goalData)
  }

  editGoal(goal) {
    let goalData = new FormData()
    goalData.append("target", goal.goalFormControl)
    
    axios.put('http://localhost:5000/api/v1.0/goals/' + goal.id, goalData)
  }
}
