import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class GoalService {

  private goal_private_list;
  private goalSubject = new Subject();
  goal_list = this.goalSubject.asObservable();

  percentageComplete;

  constructor(private http: HttpClient) { }


  getGoal(user_id) {
    return this.http.get('http://localhost:5000/api/v1.0/' + user_id + '/goals')
    .subscribe(response => { 
        this.goal_private_list = response;
        this.goalSubject.next(this.goal_private_list);
    });
    
  }
}
