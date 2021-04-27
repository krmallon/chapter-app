import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { AuthService } from '../auth.service';
import { GroupService } from '../services/group.service';
import { NotificationService } from '../services/notification.service';
import { SearchService } from '../services/search.service';

@Component({
  selector: 'app-groups',
  templateUrl: './groups.component.html',
  styleUrls: ['./groups.component.scss']
})
export class GroupsComponent implements OnInit {

  public sessionStorage = sessionStorage;
  userSearchForm;
  newGroupForm;

  constructor(public groupService: GroupService, public notifyService: NotificationService, public searchService: SearchService, public authService: AuthService, private formBuilder: FormBuilder) { }

  ngOnInit(): void {

    this.userSearchForm = this.formBuilder.group({
      query: ['', Validators.required]
    })

    this.newGroupForm = this.formBuilder.group({
      name: ['', Validators.required],
      description: ['', Validators.required]
    })

    this.groupService.getAllGroups()
    this.groupService.getGroupsByUser(sessionStorage.user_id)
  }

  isInvalid(control) {
    return this.newGroupForm.controls[control].invalid &&
           this.newGroupForm.controls[control].touched;
  }

  isUnTouched() {
    return this.newGroupForm.controls.name.pristine && this.newGroupForm.controls.description.pristine
  }

  isIncomplete() {
    return this.isInvalid('name') || this.isInvalid('description') || this.isUnTouched();
  }

  searchFormInvalid(control) {
    return this.userSearchForm.controls[control].invalid &&
           this.userSearchForm.controls[control].touched;
  }

  searchFormIncomplete() {
    return this.searchFormInvalid('query') || this.searchFormUnTouched();
  }

  searchFormUnTouched() {
    return this.userSearchForm.controls.query.pristine
  }

  onCreate() {
    this.groupService.createGroup(this.newGroupForm.value);
    this.notifyService.showSuccess('Group created', 'Success')
  }
}
