# References

Use these sources to justify the data, detection/tracking components, trained baseline, explainability, and implementation stack. Add access dates for web resources in the final report and cite the exact model weights used.

## Dataset and project context

1. U.S. Department of Transportation Intelligent Transportation Systems Joint Program Office. *Intersection Safety Challenge Stage 1B Dataset: Validation Data.* [Official validation page](https://data.transportation.gov/Roadways-and-Bridges/Intersection-Safety-Challenge-Stage-1B-Validation-/j58q-ymi4). DOI: [10.21949/1404202](https://doi.org/10.21949/1404202).
2. U.S. Department of Transportation Intelligent Transportation Systems Joint Program Office. *U.S. DOT Intersection Safety Challenge Stage 1B: System Assessment and Virtual Testing Open Data.* [Data story](https://data.transportation.gov/stories/s/U-S-DOT-Intersection-Safety-Challenge-Stage-1B-Sys/smqb-i5sx/).
3. U.S. DOT ITS Joint Program Office. *Intersection Safety Challenge.* [Official challenge overview](https://www.its.dot.gov/research-areas/intersection-safety/challenge/).

## Methods

4. J. Redmon, S. Divvala, R. Girshick, and A. Farhadi. “You Only Look Once: Unified, Real-Time Object Detection.” CVPR, 2016. [Paper](https://openaccess.thecvf.com/content_cvpr_2016/html/Redmon_You_Only_Look_CVPR_2016_paper.html). LiveCross will use a selected pretrained YOLO-family detector; the exact model, weights, and license remain to be recorded after comparison.
5. A. Bewley, Z. Ge, L. Ott, F. Ramos, and B. Upcroft. “Simple Online and Realtime Tracking.” ICIP, 2016. [Paper](https://arxiv.org/abs/1602.00763). Candidate reference for lightweight box/track association; final tracker choice remains open.
6. C. Cortes and V. Vapnik. “Support-vector networks.” *Machine Learning*, 20, 273–297, 1995. [DOI](https://doi.org/10.1007/BF00994018). Basis for the linear SVM interaction classifier.
7. R. Girshick, J. Donahue, T. Darrell, and J. Malik. “Rich feature hierarchies for accurate object detection and semantic segmentation.” CVPR, 2014. [Paper](https://arxiv.org/abs/1311.2524). Background for hard-negative mining in detector training; LiveCross will adapt the general idea to reviewed safe interaction windows and document that adaptation.
8. S. M. Lundberg and S.-I. Lee. “A Unified Approach to Interpreting Model Predictions.” NeurIPS, 2017. [Paper](https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html). General explainability reference. The initial LiveCross explanation uses directly inspectable rules and linear SVM feature contributions; SHAP is not required for the MVP.

## Software documentation

9. OpenCV. [Official documentation](https://docs.opencv.org/).
10. PyTorch. [Official documentation](https://pytorch.org/docs/stable/index.html).
11. scikit-learn. [Official documentation](https://scikit-learn.org/stable/).
12. Streamlit. [Official documentation](https://docs.streamlit.io/).
13. Ultralytics. [Official documentation and licensing information](https://docs.ultralytics.com/). Confirm the selected package/checkpoint license before distribution; do not assume every YOLO implementation has the same terms.

## Academic integrity record

For each borrowed implementation, pretrained weight file, figure, or annotation, record its source, version, license, access date, and changes made. Clearly distinguish the DOT annotations from project-created manual event labels. This list is provisional and will be updated as implementation choices are finalized.
