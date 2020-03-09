# SIGTYP 2020 Shared Task : Prediction of Typological Features


## Data Format

The model will receive the language code and feature names as inputs and will be required to fill values for those requested features.

Input:
```
mhi      Marathi      order_of_subject,_object,_and_verb=? | number_of_genders=?
jpn      Japanese      case_syncretism=? | order_of_adjective_and_noun=?
```

The expected output is:
```
mhi      Marathi      order_of_subject,_object,_and_verb= SOV | number_of_genders=three
jpn      Japanese      case_syncretism=no_case_marking | order_of_adjective_and_noun=demonstrative-Noun
```
## Data

The model will have access to typology features across a set of languages. These features are derived from the WALS database. For the purpose of this shared task, we will provide a subset of languages/features as shown below:
```
tur      Turkish      case_syncretism=no_syncretism | order_of_subject,_object,_and_verb= SOV | number_of_genders=none | definite_articles=no_definite_but_indefinite_article
hin      Hindi      case_syncretism=core_and_non_core | order_of_subject,_object,_and_verb= SOV | number_of_genders=two | definite_articles=no_definite_but_indefinite_article
urd      Urdu      order_of_subject,_object,_and_verb= SOV | definite_articles=no_definite_but_indefinite_article
jpn      Japanese      order_of_subject,_object,_and_verb= SOV | prefixing_vs_suffixing_in_inflectional_morphology=strongly_suffixing
```
Column 1: Language ID

Column 2: Language name

Column 3: It contains the feature-value pairs for each language, where features are separated by ‘|’
