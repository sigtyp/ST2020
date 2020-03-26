# SIGTYP 2020 Shared Task : Prediction of Typological Features

To participate in the shared task, you will build a system that can predict typological properties of languages, given a handful of observed features. Training examples and development examples will be provided. All submitted systems will be compared on a held-out test set.

## Data Format

The model will receive the language code, name, latitude, longitude, genus, family, country code, and feature names as inputs and will be required to fill values for those requested features.

Input:
```
mhi      Marathi      19.0      76.0      Indic      Indo-European      IN      order_of_subject,_object,_and_verb=? | number_of_genders=?
jpn      Japanese      37.0      140.0      Japanese      Japanese      JP      case_syncretism=? | order_of_adjective_and_noun=?
```

The expected output is:
```
mhi      Marathi      19.0      76.0      Indic      Indo-European      IN      order_of_subject,_object,_and_verb= SOV | number_of_genders=three
jpn      Japanese      37.0      140.0      Japanese      Japanese      JP      case_syncretism=no_case_marking | order_of_adjective_and_noun=demonstrative-Noun
```
## Data

The model will have access to typology features across a set of languages. These features are derived from the [WALS database](https://wals.info/). For the purpose of this shared task, we will provide a subset of languages/features as shown below:
```
tur      Turkish      39.0      35.0      Turkic      Altaic      TR      case_syncretism=no_syncretism | order_of_subject,_object,_and_verb= SOV | number_of_genders=none | definite_articles=no_definite_but_indefinite_article
jpn      Japanese      37.0      140.0      Japanese      Japanese      JP      order_of_subject,_object,_and_verb= SOV | prefixing_vs_suffixing_in_inflectional_morphology=strongly_suffixing
```
Column 1: Language ID

Column 2: Language name

Column 3: Latitude

Column 4: Longitude

Column 5: Genus

Column 6: Family

Column 7: Country Codes

Column 8: It contains the feature-value pairs for each language, where features are separated by ‘|’
