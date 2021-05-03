import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import config from '../config';

@Injectable({
  providedIn: 'root'
})
export class AchievementService {

  private user_achievements_private_list;
  private userAchievementsSubject = new Subject();
  user_achievement_list = this.userAchievementsSubject.asObservable();

  private achievements_private_list;
  private achievementsSubject = new Subject();
  achievement_list = this.achievementsSubject.asObservable();

  constructor(private http: HttpClient) { }

  getUserAchievements(user_id) {
    return this.http.get(config.app_url + 'user/' + user_id + '/achievements').subscribe(
        response => {
            this.user_achievements_private_list = response;
            this.userAchievementsSubject.next(this.user_achievements_private_list);
        }
    )
}

 getAllAchievements() {
  return this.http.get(config.app_url + 'achievements').subscribe(
    response => {
        this.achievements_private_list = response;
        this.achievementsSubject.next(this.achievements_private_list);
        console.log(response)
    })
}
}
