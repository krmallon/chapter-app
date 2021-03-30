import { Component, OnInit } from '@angular/core';
import { AuthService } from '../auth.service';
import { GroupService } from '../services/group.service';

@Component({
  selector: 'app-groups',
  templateUrl: './groups.component.html',
  styleUrls: ['./groups.component.scss']
})
export class GroupsComponent implements OnInit {

  constructor(public groupService: GroupService, public authService: AuthService) { }

  ngOnInit(): void {
    this.groupService.getAllGroups()
    this.groupService.getGroupsByUser(sessionStorage.user_id)
  }

}
