import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import axios from 'axios';
import { Subject } from 'rxjs';
import config from '../config';

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
    return this.http.get(config.app_url + 'groups')
    .subscribe(response => { 
        this.groups_private_list = response;
        this.groupsSubject.next(this.groups_private_list);
    });
  }

  getGroupsByUser(user_id) {
    return this.http.get(config.app_url + 'user/' + user_id +'/groups')
    .subscribe(response => { 
        this.user_groups_private_list = response;
        this.userGroupSubject.next(this.user_groups_private_list);
    });
}

  getMembers(group_id) {
    return this.http.get(config.app_url + 'groups/' + group_id + '/members')
    .subscribe(response => { 
        this.members_private_list = response;
        this.memberSubject.next(this.members_private_list);
    });
  }

  getGroup(group_id) {
    return this.http.get(config.app_url + 'groups/' + group_id)
    .subscribe(response => { 
        this.group_private_list = response;
        this.groupSubject.next(this.group_private_list);
    });
  }

  getPosts(group_id) {
    return this.http.get(config.app_url + 'groups/' + group_id + '/posts')
    .subscribe(response => {
      this.posts_private_list = response;
      this.postsSubject.next(this.posts_private_list)
      console.log(response)
    })
  }

  createGroup(group) {
    let groupData = new FormData()
    groupData.append("name", group.name)
    groupData.append("description", group.description)
    groupData.append("founder_id", sessionStorage.user_id)
    axios.post(config.app_url + 'groups/new', groupData)
  }

  joinGroup(group_id) {
    let joinData = new FormData();
    joinData.append("user_id", sessionStorage.user_id)
    axios.post(config.app_url + 'groups/' + group_id + '/join', joinData)
  }

  createPost(group_id, post) {
    let postData = new FormData();
    postData.append("title", post.title)
    postData.append("text", post.text)
    postData.append("user_id", sessionStorage.user_id)

    axios.post(config.app_url + 'groups/' + group_id + '/posts', postData)
  }
}
