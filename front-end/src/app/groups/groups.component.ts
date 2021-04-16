import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { AuthService } from '../auth.service';
import { GroupService } from '../services/group.service';
import { SearchService } from '../services/search.service';

@Component({
  selector: 'app-groups',
  templateUrl: './groups.component.html',
  styleUrls: ['./groups.component.scss']
})
export class GroupsComponent implements OnInit {

  public sessionStorage = sessionStorage;
  userSearchForm;

  constructor(public groupService: GroupService, public searchService: SearchService, public authService: AuthService, private formBuilder: FormBuilder) { }

  ngOnInit(): void {

    this.userSearchForm = this.formBuilder.group({
      query: ['', Validators.required]
    })

    this.groupService.getAllGroups()
    this.groupService.getGroupsByUser(sessionStorage.user_id)
  }

}
