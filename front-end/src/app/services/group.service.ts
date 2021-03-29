import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class GroupService {

  private group_private_list;
  private groupSubject = new Subject();
  group_list = this.groupSubject.asObservable();

  private groups_private_list;
  private groupsSubject = new Subject();
  groups_list = this.groupsSubject.asObservable();

  private user_groups_private_list;
  private userGroupSubject = new Subject();
  user_groups_list = this.userGroupSubject.asObservable();

  private members_private_list;
  private memberSubject = new Subject();
  members_list = this.memberSubject.asObservable();

  private posts_private_list;
  private postsSubject = new Subject();
  posts_list = this.postsSubject.asObservable();

  constructor(private http: HttpClient) { }

  getAllGroups() {
    return this.http.get('http://localhost:5000/api/v1.0/groups')
    .subscribe(response => { 
        this.groups_private_list = response;
        this.groupsSubject.next(this.groups_private_list);
    });
  }

  getGroupsByUser(user_id) {
    return this.http.get('http://localhost:5000/api/v1.0/user/' + user_id +'/groups')
    .subscribe(response => { 
        this.user_groups_private_list = response;
        this.userGroupSubject.next(this.user_groups_private_list);
    });
}

  getMembers(group_id) {
    return this.http.get('http://localhost:5000/api/v1.0/groups/' + group_id + '/members')
    .subscribe(response => { 
        this.members_private_list = response;
        this.memberSubject.next(this.members_private_list);
    });
  }

  getGroup(group_id) {
    return this.http.get('http://localhost:5000/api/v1.0/groups/' + group_id)
    .subscribe(response => { 
        this.group_private_list = response;
        this.groupSubject.next(this.group_private_list);
    });
  }

  getPosts(group_id) {
    return this.http.get('http://localhost:5000/api/v1.0/groups/' + group_id + '/posts')
    .subscribe(response => {
      this.posts_private_list = response;
      this.postsSubject.next(this.posts_private_list)
    })

  }
}
