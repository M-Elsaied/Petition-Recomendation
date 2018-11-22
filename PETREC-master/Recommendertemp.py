import pandas as pd
import numpy as np
# import the functions for cosine distance, euclidean distance
from scipy.spatial.distance import cosine, euclidean, correlation
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


# define a functions, which takes the given item as the input and returns the top K similar items (in a data frame)
def top_k_items(dense_matrix, item_number, k):
    # copy the dense matrix and transpose it so each row represents an item
    df_sim = dense_matrix.transpose()
    # remove the active item
    df_sim = df_sim.loc[df_sim.index != item_number]
    # calculate the distance between the given item for each row (apply the function to each row if axis = 1)
    df_sim["distance"] = df_sim.apply(lambda x: euclidean(dense_matrix[item_number], x), axis=1)
    # return the top k from the sorted distances
    return df_sim.sort_values(by="distance").head(k)["distance"]


# define a functions, which takes the given user as the input and returns the top K similar users (in a data frame)
def top_k_users(dense_matrix, user_number, k):
    # no need to transpose the matrix this time because the rows already represent users
    # remove the active user
    df_sim = dense_matrix.loc[dense_matrix.index != user_number]
    # calculate the distance for between the given user and each row
    df_sim["distance"] = df_sim.apply(lambda x: euclidean(dense_matrix.loc[user_number], x), axis=1)
    # return the top k from the sorted distances
    return df_sim.sort_values(by="distance").head(k)["distance"]


# please note that I have changed this function in the ml_100k.py a little. Now this function has two
# additional arguments: k (i.e., the number of similar user) with the default value 5, and item_number that
# represent the number of the item. You want to predict the rating the user will give to the item.
def user_based_predict(df_train_x, df_test_x, df_train_y, user_number, item_number, k):
    # copy from all the training predictors
    df_sim = df_train_x.copy()
    # for each user, calculate the distance between this user and the active user
    df_sim["distance"] = df_sim.apply(lambda x: euclidean(df_test_x.loc[user_number], x), axis=1)
    # create a new data frame to store the top k similar users
    df_sim_users = df_sim.loc[df_sim.sort_values(by="distance").head(k).index]
    # calculate these similar users' rating on a given item, weighted by distance
    df_sim_users["weighed_d"] = map(lambda x: df_sim_users.loc[x]["distance"] * df_train_y.loc[x][item_number],
                                    df_sim_users.index)
    predicted = df_sim_users["weighed_d"].sum() / df_sim_users["distance"].sum()

    return predicted


def main():
    df_data1 = pd.read_csv("C:/Users/MSW2755/Desktop/INFS 770/INFS770_assignment3/DBbook_train_ratings.tsv",
                           sep="\t")
    dense_matrix = df_data1.pivot_table(values="rate", index=["userID"], columns=["itemID"], aggfunc=np.sum)

    print dense_matrix.isnull().sum().sum()
    print dense_matrix.notnull().sum().sum()

    dense_matrix = dense_matrix.fillna(0)

    Computing
    correlation
    distance
    between
    users
    2 & 3


print correlation(dense_matrix.loc[2], dense_matrix.loc[3])

print correlation(dense_matrix[1], dense_matrix[36])

print cosine(dense_matrix[1], dense_matrix[36])

print top_k_items(dense_matrix, 8010, 5)

df_item_freq = df_data1.groupby("itemID").count()
df_user_freq = df_data1.groupby("userID").count()
selected_items = df_item_freq[df_item_freq["userID"] > 20].index
dense_matrix = dense_matrix[selected_items]
selected_users = df_user_freq[df_user_freq["itemID"] > 20].index
dense_matrix = dense_matrix.loc[selected_users]

# print dense_matrix[8010].value_counts()

# create a data frame for the predictors
df_x = dense_matrix[[col for col in dense_matrix.columns if col != 8010]]
print df_x.shape
df_y = dense_matrix[[8010]]
print df_y.shape

train_x, test_x, train_y, test_y = train_test_split(df_x, df_y, test_size=0.2, random_state=0)
df_train_x = pd.DataFrame(train_x, columns=df_x.columns)
df_test_x = pd.DataFrame(test_x, columns=df_x.columns)
df_train_y = pd.DataFrame(train_y, columns=[8010])
df_test_y = pd.DataFrame(test_y, columns=[8010])

print "Train x:"
print df_train_x.shape

print "Test x:"
print df_test_x.shape

print "Train y:"
print df_train_y.shape

print "Test y:"
print df_test_y.shape

print df_test_y.mean(0)

pred_8010 = []
for user_number in df_test_x.index:
    predicted = user_based_predict(df_train_x, df_test_x, df_train_y, user_number, 8010, k=10)
    pred_8010.append(predicted)

new_pred = user_based_predict(df_train_x, df_test_x, df_train_y, df_test_x.index[23], 8010, k=10)
# print new_pred

user_number = df_test_x.index[23]
user_24_8010 = user_based_predict(df_train_x, df_test_x, df_train_y, user_number, 8010, 10)

print user_24_8010
print df_test_y.loc[user_number][8010]

print mean_squared_error(df_test_y, pred_8010)
print (mean_squared_error(df_test_y, pred_8010)) ** 0.5

return

if __name__ == "__main__":
    main()

# Compute Rank
'''
for i in range(m):
for j in range(n):
    print RStar[i][j]

lr=[]
lind=[]
for x in range(0, T.shape[0]):
    yList = []
    list=[]
    for y0 in range(0, T.shape[1]):
        yList.append(y0)
        list.append(RStar[x, y0])

    sorted=False
    while not sorted:
        sorted = True  # Assume the list is now sorted
        for y1 in range(0, T.shape[1]-1):
            if list[y1] < list[y1+1]:
                sorted = False  # We found two elements in the wrong order
                hold = list[y1 + 1]
                list[y1 + 1] = list[y1]
                list[y1] = hold
                hold1 = yList[y1 + 1]
                yList[y1 + 1] = yList[y1]
                yList[y1] = hold1

    lr.append(list)
    lind.append(yList)

count=0
mrr=float(0)
for x in range(0, T.shape[0]):
    for y in range(0, T.shape[1]):
        if T[x, y]==1:
            for i in range(0,len(lind[x])):
                if y==lind[x][i]:
                    break
            mrr+=float(float(1)/float(i+1))
            count+=1
mrr/=float(count)
print 'mrr = '+str(mrr)
'''