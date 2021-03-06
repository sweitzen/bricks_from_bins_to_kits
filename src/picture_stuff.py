from PIL import Image, ImageOps
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import cv2
import os.path
import sys
import datetime

'''
Capstone project for Galvanize Data Science Immersion course, Seattle
Brian Silverstein, 2017
Ben's Bricks BINS TO BRICKS App

This file will take functions currently in CNN_tensor_flow_legos.ipynb
'''



def get_image(image_path,image_default_size=299):
    '''FIX THIS TO LOAD AND RESIZE WITH INPUTS image_path,N_PIXELS
       SEE FILE Process_pictures_pickle.ipynb
    '''
    """Get a numpy array of an image so that one can access values[x][y].
       INPUT:  str path to saved image file
       OUTPUT: numpy array of image pixels
    """
    image = Image.open(image_path, 'r')
    width, height = image.size
    if (width != image_default_size) or (height != image_default_size):
        # RESIZE
        image = image.resize((image_default_size,image_default_size),
                             Image.ANTIALIAS)
        width, height = image_default_size,image_default_size
    pixel_values = list(image.getdata())
    if image.mode == 'RGB':
        channels = 3
    elif image.mode == 'L':
        channels = 1
    else:
        print("Unknown mode: %s" % image.mode)
        return None
    pixel_values = np.array(pixel_values).reshape((width, height, channels))
    return pixel_values


def remove_grid_lines(axs):
    """Remove the default grid lines from a collection of axies.
       INPUT:  matplotlib axis set
       OUTPUT: none"""
    for ax in axs.flatten():
        ax.grid(False)

def convert_to_gray(X):
    '''Converts numpy array of N RGB pictures of dimension mxn (times 3 colors)
       and returns a numpy array of the same dimensions where all channels are
       the same
       INPUT:  X, numpy array
       OUTPUT: X_gray, numpy array
    '''
    X_gray = np.mean(X, -1).astype(np.uint8)
    X_gray = np.expand_dims(X_gray, axis=-1)
    X_gray = np.concatenate([X_gray, X_gray, X_gray],axis=-1)
    return X_gray

def initialize_camera():
    ''' For use with OpenCV2 (import cv2)
        INPUTS: None
        OUTPUT: cv2 camera object
    '''
    print "checkpoint - initialize camera now"
    sys.stdout.flush()
    return cv2.VideoCapture(0)



def increment_filename(pic_label,extension=1):
    '''Creates a filename to store picture in, based on brick label
       and increments through allowable file name-number combinations
       until it reaches one that doesn't already exist
       INPUTS: pic_label: string, name for base of file
               extension: integer, number for file index
       OUTPUT: updated integer extension, and string file name
    '''
    #check if this file name exists
    filename = _add_tail(pic_label,extension)
    print 'testing:', filename
    while os.path.isfile(filename):
        print filename, "exists"
        extension +=1
        filename = _add_tail(pic_label,extension)
    print "Save next picture as: ",filename
    return extension, filename

def _add_tail(pic_label,extension):
    '''Create a file name with 3-digit integer number and .jpeg extension
       based on base name
       INPUTS: pic_label: string, name for base of file
               extension: integer, number for file index
       OUTPUT: string file name
    '''
    tail = '-{0:03d}.jpeg'.format(extension)
    filename = '../brick_pic_temp_files/' + str(pic_label) + tail
    return filename



def shoot_1_pic(camera):
    '''Shoots 1 picture with the webcam with OpenCV2
       INPUTS: camera object
       OUTPUT: image in PIL format
    '''
    image_stuff, image = camera.read()
    return image

def shoot_pic(camera,npics=20):
    '''Shoots several pics to give webcam time to adjust light, then
       saves and returns final image
       INPUTS: camera object, number of shots to take
       OUTPUT: image in PIL format
    '''
    for i in range(npics):
        capture = shoot_1_pic(camera)
    return capture

def shoot_crop_and_scale(camera,use_gray=True,image_dims=299,border_fraction=0.3):
    # Shoot picture, crop and scale
    pic = shoot_pic(camera)
    return crop_and_scale(pic,use_gray,image_dims,border_fraction)

def crop_and_scale(pic,use_gray=True,image_dims=299,border_fraction=0.3):
    if use_gray:
        pic = convert_to_gray(pic)
    im = Image.fromarray(pic)
    newpic = ImageOps.fit(im, (image_dims,image_dims), Image.ANTIALIAS,
                          border_fraction, (.5,.5))
    return np.array(newpic)

def picture_index_function(y_list):
    ''' Given the set of example pictures associated with y_list labels,
        make a dictionary that lets you pick the right photo from a label
        This will NOT be the same dictionary as on the training set.

        X[[picture_index_lookup[label]] is the picture for the label

        INPUT:  y_list, list of labels for picture classes
        OUTPUT: picture_index_lookup, dictionary keys are indices
                                      dixtionary valuess are labels
    '''

    picture_index_lookup = {}
    for idx,label in enumerate(y_list):
        picture_index_lookup[label]=idx
    return picture_index_lookup


def save_pic(filename,capture):
    '''Save previously captured image to file
    '''
    cv2.imwrite(filename, capture)


def keep_shooting_until_acceptable(camera,filename):
    '''Takes a webcam photo and loops until user finds it acceptable.
       User can enter 0 to reshoot, or anything else in order to save
       the file and use it for image classification.
       INPUTS: camera: OpenCV2 video capture object
               filename: path and name to save picture
       OUTPUT: one_pic_X: numpy array of new photo
    '''
    keep_shooting = True
    while keep_shooting:
        one_pic_X = shoot_crop_and_scale(camera,use_gray=True)

        fig, ax = plt.subplots(1,figsize=(6,6))
        # NOTE: one_pic_X[:,:,::-1] is presented this way because of OpenCV's
        # preference to treat RGB files as BGR, so they need to be reversed.
        # This isn't needed if we stick to grayscale.
        ax.imshow(one_pic_X[:,:,::-1], cmap=plt.cm.gray_r, interpolation="nearest")
        ax.grid(False)
        plt.show();

        next_action = raw_input('Enter 0:reshoot, any other:save')

        if next_action != '0':
            save_pic(filename,one_pic_X)
            keep_shooting = False

    return one_pic_X


def y_to_hot(y_list):
    '''Convert a list of category labels to a 1-hot numpy array
       INPUT:  y_list: list of integers containing category labels
       OUTPUTS:label_dic: a dictionary whose length is the same as
                   the unique values in y_list, whose keys are integer
                   indices and values are y_list values
               y_out: a 1-hot numpy array whose length is the same as
                   y_list and width are the number of items in label_dic
    '''
    y_out =[]
    label_dic={}
    d2={}
    for idx,val in enumerate(np.unique(y_list)):
        label_dic[idx]=val
        d2[val]=idx
    y_out = np.zeros((len(y_list),len(label_dic)),dtype=int)
    for idx,val in enumerate(y_list):
        y_out[idx,d2[val]]=1
    return label_dic,y_out


def make_full_prediction_list(predict_gen,label_dic,n_match=5):
    '''Takes a list of item labels and predicted values and returns a
       list of prediction labels for the first n_match predictions
       INPUTS: y_list,
               predict_gen,
               n_match=5
       OUTPUTS:out_list = list of list of predictions
               out_weights = numpy array of top n_match predicted weights
    '''
    temp0 = np.flip(np.argsort(predict_gen, axis=1),axis=1)
    out_weights = np.flip(np.sort(predict_gen,axis = 1),axis=1)[:,:n_match]

    out_list=[]
    for idx in range(len(predict_gen)):
        preds = [label_dic[temp0[idx,idx2]] for idx2 in range(n_match)]
        out_list.append(preds)
    return out_list,out_weights

def make_one_prediction_list(predict_gen,label_dic,n_match=5):
    '''Takes a list of item labels and predicted values and returns a
       list of prediction labels for the first n_match predictions
       NOTE: because predict_gen uses model.predict_on_batch, which is
             designed to return predictions for a list of inputs, this
             function has to return out_list[0],out_weights[0] as the
             predictions associated with the first and only input.
       INPUTS: y_list,
               predict_gen,
               n_match=5
       OUTPUTS:out_list = list of list of predictions
               out_weights = numpy array of top n_match predicted weights
    '''
    temp0 = np.flip(np.argsort(predict_gen, axis=1),axis=1)
    out_weights = np.flip(np.sort(predict_gen,axis = 1),axis=1)[:,:n_match]

    out_list=[]
    for idx in range(len(predict_gen)):
        preds = [label_dic[temp0[idx,idx2]] for idx2 in range(n_match)]
        out_list.append(preds)
    return out_list[0],out_weights[0]


def clear_old_pictures(hours=1):
    '''Deletes any pictures in the static/images/saved_brick_predictions/
       which are more than hours old
       INPUT:  hours, integer, default hours=1
       OUTPUT: none
    '''
    dir_to_search = "static/images/saved_brick_predictions/"

    for dirpath, dirnames, filenames in os.walk(dir_to_search):
       for file in filenames:
           if file[-4:]==".png":
              curpath = os.path.join(dirpath, file)
              file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(curpath))
              if datetime.datetime.now() - file_modified > datetime.timedelta(hours=2):
                  print file,file_modified
                  os.remove(curpath)

def make_wrong_list(y_hot,full_prediction_list,label_dic):
    '''Takes a list of item labels and predicted values and returns a
       list of labels and predictions for items which were wrong in
       the first n_match predictions
       INPUTS: y_list,
               predict_gen,
               n_match=5
       OUTPUTS:wrong_list = list of lists
               containing item labels followed by list of predictions
    '''
    n_match = len(full_prediction_list[0])
    #label_dic,y_hot = y_to_hot(y_list)
    wrong_list=[]
    for idx in range(len(y_hot)):
        actual = label_dic[np.argmax(y_hot[idx])]
        if actual not in full_prediction_list[idx]:
            wrong_list.append([actual, full_prediction_list[idx]])
    return wrong_list
