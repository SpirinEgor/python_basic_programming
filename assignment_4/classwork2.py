import numpy
from sklearn.datasets import fetch_openml
from sklearn.metrics import f1_score
from sklearn.svm import SVC

X, Y = fetch_openml('mnist_784', return_X_y=True)
print(f"shape of X is {X.shape}")

test_shuffle = numpy.random.permutation(X.shape[0])

# I have a memory allocation error if X/Y_train size is > 35k using SVC
# SVC with C=10 gives 0.9811 result
# Other models give a worse result (~0.96)
X_test, X_train = X[test_shuffle[:10000]], X[test_shuffle[10000:45000]]
Y_test, Y_train = Y[test_shuffle[:10000]], Y[test_shuffle[10000:45000]]

print(f"train size: {X_train.shape[0]}")
print(f"test size: {X_test.shape[0]}")

model = SVC(C=10, random_state=7)
model.fit(X_train, Y_train)

y_pred = model.predict(X_test)
print(f"test score is {f1_score(Y_test, y_pred, average='micro')}")
