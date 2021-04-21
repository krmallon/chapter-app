import { Component, OnInit } from '@angular/core';
import { RecommendationService } from '../services/recommendation.service';

@Component({
  selector: 'app-recommendations',
  templateUrl: './recommendations.component.html',
  styleUrls: ['./recommendations.component.scss']
})
export class RecommendationsComponent implements OnInit {

  recommendationsExist;

  constructor(public recommendationService: RecommendationService) { }

  ngOnInit(): void {
    this.recommendationService.getRecommendations(sessionStorage.user_id)
    // this.recommendationService.recommendationsExist()
    // this.recommendationsExist = this.recommendationService.recommendationsExist()
    // this.recommendationService.recommendationsExist()
  }

  // recommendationsExist() {
  //   return this.recommendationService.books_list.length 
  // }
}
