import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { AuthService } from '../auth.service';
import { SearchService } from '../services/search.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-nav',
  templateUrl: './nav.component.html',
  styleUrls: ['./nav.component.scss']
})
export class NavComponent implements OnInit {

  public sessionStorage = sessionStorage;
  searchForm;
  brand = "Chapter"

  constructor(public authService: AuthService, public formBuilder: FormBuilder, public searchService: SearchService, private router: Router) { }

  ngOnInit(): void {
    this.searchForm = this.formBuilder.group({
      query: ['', Validators.required]
    })
  }

  onSearch() {
    this.searchService.searchBooks(this.searchForm.value.query, 0, 'en', 'relevance')
    this.router.navigateByUrl('search/books/' + this.searchForm.value.query)
  }

}
