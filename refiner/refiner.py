from PIL import Image
import numpy as np
from argparse import ArgumentParser
import time
import os
from scipy import linalg
import random
import shutil

FLAG_python = True

regular_size = (256, 256)
patch_size=(64, 64)
patch_number = (regular_size[0]//patch_size[0])*(regular_size[1]//patch_size[1])
FeatureNumber = 256

def make_regular_image(img):
    return img.resize(regular_size).convert('RGB')

def calc_hist(img):
    w, h = img.size
    patch_w, patch_h = patch_size
    assert w%patch_w == h%patch_h == 0

    hist_dict = dict()
    index = 0

    for i in xrange(0, w, patch_w):
        for j in xrange(0, h, patch_h):
            subimg = img.crop((i, j, i+patch_w, j+patch_h)).copy()
            hist_dict[index] = subimg.histogram()
            index+=1

    return hist_dict

def _get_files_abspath_from_directory(fdirname):
    fname_list = os.listdir(fdirname)
    fpath_list = list()

    for fname in fname_list:
        fpath = fdirname + '/' + fname
        if os.path.isfile(fpath):
            fpath_list.append(fpath)

    return fpath_list

def _get_infos_from_textfile(fname):
    info_list = list()

    fid = open(fname, 'r')
    lines = fid.readlines()
    for eachline in lines:
        eachline = eachline.strip()
        if not eachline.startswith('#') and len(eachline):
            info_list.append(eachline)
    fid.close()

    return info_list

def _get_images_path(file_path_list):
    img_path_list = list()

    for filepath in file_path_list:
        if not os.path.exists(filepath):
            print filepath, 'not exist'
            continue

        if filepath.endswith('.jpg') or filepath.endswith('.JPEG'):
            img_path_list.append(filepath)
        else:
            print 'Not a jpg or JPEG', filepath

    return img_path_list

def _extract_image_features(img_path_list):
    stime = time.time()
    feature_dict = dict()
    img_valid_path_list = list()

    for patch in range(0, patch_number):
        feature_dict[patch] = list()

    for index in range(0, len(img_path_list)):
        imgpath = img_path_list[index]
        try:
            img = make_regular_image(Image.open(imgpath))

            hist_dict = calc_hist(img)

            assert len(hist_dict) == patch_number

            img_valid_path_list.append(imgpath)

            for patch in range(0, patch_number):
                feature_dict[patch].append(hist_dict[patch])

        except Exception,e:
            print Exception, ":", e, imgpath
            # remove broken images
            os.remove(imgpath)

        if (index%1000)==0:
            print("image %d (%d)" % (index, len(img_path_list)))
            print("--- extract image features cost %s seconds ---" % (time.time() - stime))

    return feature_dict, img_valid_path_list

def PCA(data, dims_rescaled_data):
    # mean center the data
    m = data.mean(axis=0)
    data -= m
    # calculate the covariance matrix
    R = np.cov(data, rowvar=False)
    # calculate eigenvectors and eigenvalues of the covariance matrix
    # use 'eigh' rather than 'eig' since R is symmetric
    evals, evecs = linalg.eigh(R)
    # sort eigenvalue in decreasing order and sort eigenvectors according to same index
    indices = np.argsort(evals)[::-1]
    evals = evals[indices]
    evecs = evecs[:, indices]
    # select the first n eigenvectors (n is desired dimension of rescaled data array, or dims_rescaled_data)
    if dims_rescaled_data:
        evecs = evecs[:,:dims_rescaled_data]
        print np.sum(evals[:dims_rescaled_data])/np.sum(evals)
    # carry out the transformation on the data using eigenvectors
    # and return the re-scaled data, eigenvectors, and data mean
    return np.dot(data, evecs), evecs, m

def _feature_compression(feature_dict, dims):
    compressed_feature_dict = dict()
    evecs_dict = dict()
    imgmean_dict = dict()

    for patch in range(0, patch_number):
        compressed_feature_dict[patch], evecs_dict[patch], imgmean_dict[patch] = PCA(np.array(feature_dict[patch]), dims)

    return compressed_feature_dict, evecs_dict, imgmean_dict

def _feature_projection(feature_dict, evecs_dict, imgmean_dict):
    projected_feature_dict = dict()

    for patch in range(0, patch_number):
        projected_feature_dict[patch] = np.dot((feature_dict[patch] - imgmean_dict[patch]), evecs_dict[patch])

    return projected_feature_dict

def _calc_corr_coef_basic(feature_dict):
    corr_coef = np.corrcoef(feature_dict[0])
    for patch in range(1, patch_number):
        corr_coef += np.corrcoef(feature_dict[patch])
    # remove diagonal elements and corrcoef is symmetric matrix, get lower triangle of a symmetric matrix
    corr_coef = np.tril(corr_coef, -1)

    return corr_coef/patch_number

def _calc_corr_coef_advance(feature_dict_1, feature_dict_2):
    corr_coef = np.corrcoef(feature_dict_1[0], feature_dict_2[0])
    for patch in range(1, patch_number):
        corr_coef += np.corrcoef(feature_dict_1[patch], feature_dict_2[patch])
    # get top-right area
    corr_coef = corr_coef[0:feature_dict_1[0].shape[0], feature_dict_1[0].shape[0]:corr_coef.shape[0]]

    return corr_coef/patch_number

def _get_similar_items_basic(corr_coef, thres):
    simi_item_pair_list = np.argwhere(corr_coef > thres)
    print('threshold %.2f simi_item_pair_list size %d' % (thres, len(simi_item_pair_list)))

    simi_set_dict = dict()
    simi_item_dict = dict()

    for item in simi_item_pair_list:
        flag_found = False
        for index in range(0, len(simi_set_dict)):
            if set(item) & simi_set_dict[index]:
                simi_set_dict[index].update(set(item))
                flag_found = True

        if not flag_found:
            simi_set_dict[len(simi_set_dict)] = set(item)

    for index in simi_set_dict:
        item_list = list(simi_set_dict[index])
        simi_item_dict[item_list[0]] = item_list[1:len(item_list)]

    print('threshold %.2f simi_item_dict size %d' % (thres, len(simi_item_dict)))
    return simi_item_dict

def _get_similar_items_advance(corr_coef, thres, offset1, offset2):
    simi_item_pair_list = np.argwhere(corr_coef > thres)
    print('threshold %.2f simi_item_pair_list size %d' % (thres, len(simi_item_pair_list)))

    simi_item_dict = dict()

    for item in simi_item_pair_list:
        gt_id = item[0] + offset1
        candidate_id = item[1] + offset2

        if not simi_item_dict.has_key(gt_id):
            simi_item_dict[gt_id] = list()

        simi_item_dict[gt_id].append(candidate_id)

    print('threshold %.2f simi_item_dict size %d' % (thres, len(simi_item_dict)))
    return simi_item_dict

def combine_2_similar_item_dict(dict1, dict2):
    tempdict = dict1.copy()

    for key in dict2:
        if key in dict1:
            tempdict[key].extend(dict2[key])
        else:
            tempdict[key] = dict2[key]

    return tempdict

def _get_similar_basic(corr_coef, threshold):
    tempdict = dict()

    for thres in np.arange(threshold, 0.91, 0.05):
        tempdict[thres] = _get_similar_items_basic(corr_coef, thres)

    return tempdict

def _get_similar_advance(corr_coef, threshold, offset1, offset2, dict1):
    tempdict = dict1.copy()

    for thres in np.arange(threshold, 0.91, 0.05):
        simi_item_dict = _get_similar_items_advance(corr_coef, thres, offset1, offset2)

        if thres not in tempdict:
            tempdict[thres] = dict()

        tempdict[thres] = combine_2_similar_item_dict(tempdict[thres], simi_item_dict)

    return tempdict

def _save_refined_infos_basic(img_path_list, simi_dict, fprefix):
    # img_path_list is candidate set
    assert len(img_path_list), 'the length of img_path_list is smaller than 0'
    assert len(simi_dict), 'the length of simi_dict is smaller than 0'

    for thres in simi_dict:
        fname_discard = fprefix + '_discard_' + str(thres)
        fname_keep = fprefix + '_keep_' + str(thres)

        fid_discard = open(fname_discard, 'w')
        fid_discard.write('### images discard threshold: ' + str(thres) + ' ###' + '\n')

        img_discard_set = set()

        simi_item_dict = simi_dict[thres]

        index = 0
        for img_1_id in simi_item_dict:
            img_2_id_list = list(set(simi_item_dict[img_1_id]))
            if len(img_2_id_list):
                fid_discard.write('###'+ str(index) +'###' + '\n')
                fid_discard.write('# ' + img_path_list[img_1_id] + '\n')
                index += 1
                for img_2_id in img_2_id_list:
                    fid_discard.write(img_path_list[img_2_id] + '\n')

                img_discard_set.update(set(img_2_id_list))
        fid_discard.close()

        fid_keep = open(fname_keep, 'w')
        fid_keep.write('### images keep +' + str(len(img_path_list) - len(img_discard_set)) + '(-' + str(len(img_discard_set)) + ') threshold: ' + str(thres) + ' ###' + '\n')
        for img_2_id in range(0, len(img_path_list)):
            if img_2_id not in img_discard_set:
                fid_keep.write(img_path_list[img_2_id] + '\n')
        fid_keep.close()

        print("threshold %.2f candidate images discarded size %d kept size %d" % (thres, len(img_discard_set), len(img_path_list)-len(img_discard_set)))

def _save_refined_infos_advance(img_path_list_1, img_path_list_2, simi_dict, fprefix):
    # img_path_list_1 is authority gt set, img_path_list_2 is candidate set
    assert len(img_path_list_1), 'the length of img_path_list_1 is smaller than 0'
    assert len(img_path_list_2), 'the length of img_path_list_2 is smaller than 0'
    assert len(simi_dict), 'the length of simi_dict is smaller than 0'

    for thres in simi_dict:
        fname_discard = fprefix + '_discard_' + str(thres)
        fname_keep = fprefix + '_keep_' + str(thres)

        fid_discard = open(fname_discard, 'w')
        fid_discard.write('### images discard threshold: ' + str(thres) + ' ###' + '\n')

        img_discard_set = set()

        simi_item_dict = simi_dict[thres]
        index = 0
        for img_1_id in simi_item_dict:
            img_2_id_list = list(set(simi_item_dict[img_1_id]))
            if len(img_2_id_list):
                fid_discard.write('###'+ str(index) +'###' + '\n')
                fid_discard.write('# ' + img_path_list_1[img_1_id] + '\n')
                index += 1
                for img_2_id in img_2_id_list:
                    fid_discard.write(img_path_list_2[img_2_id] + '\n')

                img_discard_set.update(set(img_2_id_list))
        fid_discard.close()

        fid_keep = open(fname_keep, 'w')
        fid_keep.write('### images keep +' + str(len(img_path_list_2) - len(img_discard_set)) + '(-' + str(len(img_discard_set)) + ') threshold: ' + str(thres) + ' ###' + '\n')
        for img_2_id in range(0, len(img_path_list_2)):
            if img_2_id not in img_discard_set:
                fid_keep.write(img_path_list_2[img_2_id] + '\n')
        fid_keep.close()

        print("threshold %.2f candidate images discarded size %d kept size %d" % (thres, len(img_discard_set), len(img_path_list_2)-len(img_discard_set)))

def refiner_advance(gt_file_list, candidate_file_list, out_fprefix, threshold):
    stime = time.time()
    print '*************** get images path *****************'
    gt_images_list = _get_images_path(gt_file_list)
    candidate_images_list = _get_images_path(candidate_file_list)
    print("--- get images path cost %s seconds ---" % (time.time() - stime))
    print ''
    # limit the candidate_images_list size up to 10000
    if len(candidate_images_list) > 10000:
        candidate_images_list = candidate_images_list[0:10000]
        #candidate_images_list = random.sample(candidate_images_list, 10000)


    ### split candidate images into multiple batch
    candidate_batch_size = 10000
    candidate_images_number = len(candidate_images_list)
    candidate_batch_number = candidate_images_number // candidate_batch_size
    candidate_batch_number = (candidate_batch_number+1) if (candidate_images_number % candidate_batch_size) else candidate_batch_number

    #store valid images list
    candidate_images_valid_list = list()
    gt_images_valid_list = list()
    # store similar for each threshold
    similar_dict = dict()

    print("--- split candidate images (%d) into %d batch (%d)---" % (candidate_images_number, candidate_batch_number, candidate_batch_size))

    for candidate_batch_id in range(0, candidate_batch_number):
        candidate_id_start = candidate_batch_id * candidate_batch_size
        candidate_id_end = (candidate_batch_id+1) * candidate_batch_size
        if candidate_id_end > candidate_images_number:
            candidate_id_end = candidate_images_number

        print ("--- candidate batch %d images from %d to %d ---" % (candidate_batch_id, candidate_id_start, candidate_id_end))
        candidate_batch_images_list = candidate_images_list[candidate_id_start:candidate_id_end]

        stime = time.time()
        print '*************** extract candidate images features *****************'
        candidate_batch_images_feature_dict, candidate_batch_images_valid_list = _extract_image_features(candidate_batch_images_list)
        print("--- extract candidate images feature cost %s seconds ---" % (time.time() - stime))
        print ''

        ### split gt images into multiple batch
        gt_batch_size = 6000
        gt_images_number = len(gt_images_list)
        gt_batch_number = gt_images_number // gt_batch_size
        gt_batch_number = (gt_batch_number+1) if (gt_images_number % gt_batch_size) else gt_batch_number

        print("--- split gt images (%d) into %d batch (%d)---" % (gt_images_number, gt_batch_number, gt_batch_size))

        for gt_batch_id in range(0, gt_batch_number):
            gt_id_start = gt_batch_id * gt_batch_size
            gt_id_end = (gt_batch_id+1) * gt_batch_size
            if gt_id_end > gt_images_number:
                gt_id_end = gt_images_number

            print ("--- gt batch %d images from %d to %d ---" % (gt_batch_id, gt_id_start, gt_id_end))
            gt_batch_images_list = gt_images_list[gt_id_start:gt_id_end]

            stime = time.time()
            print '*************** extract gt images features *****************'
            gt_batch_images_feature_dict, gt_batch_images_valid_list = _extract_image_features(gt_batch_images_list)
            print("--- extract gt images feature cost %s seconds ---" % (time.time() - stime))
            print ''

            stime = time.time()
            print '*************** compress gt images features *****************'
            gt_batch_images_compressed_feature_dict, gt_batch_eigenvecs_dict, gt_batch_images_mean_dict = _feature_compression(gt_batch_images_feature_dict, FeatureNumber)
            print("--- compress gt images feature cost %s seconds ---" % (time.time() - stime))
            print ''

            stime = time.time()
            print '*************** project candidate images features *****************'
            candidate_batch_images_projected_feature_dict = _feature_projection(candidate_batch_images_feature_dict, gt_batch_eigenvecs_dict, gt_batch_images_mean_dict)
            print("--- project candidate images feature cost %s seconds ---" % (time.time() - stime))
            print ''

            stime = time.time()
            print '*************** calculate corrcoef *****************'
            # gt_batch_images_compressed_feature_dict must be arg1, candidate_batch_images_projected_feature_dict must be arg2
            corr_coefs = _calc_corr_coef_advance(gt_batch_images_compressed_feature_dict, candidate_batch_images_projected_feature_dict)
            print("--- calculate corrcoef cost %s seconds ---" % (time.time() - stime))
            print ''
            print 'corr_coefs', corr_coefs.shape

            stime = time.time()
            print '*************** get similar dict *****************'
            similar_dict = _get_similar_advance(corr_coefs, threshold, len(gt_images_valid_list), len(candidate_images_valid_list), similar_dict)
            print("--- get similar dict cost %s seconds ---" % (time.time() - stime))
            print ''

            gt_images_valid_list.extend(gt_batch_images_valid_list)

        candidate_images_valid_list.extend(candidate_batch_images_valid_list)

    stime = time.time()
    print '*************** save refined images infos *****************'
    # gt_images_valid_list must be arg1, candidate_images_valid_list must be arg2
    _save_refined_infos_advance(gt_images_valid_list, candidate_images_valid_list, similar_dict, out_fprefix)
    print("--- save refined images infos cost %s seconds ---" % (time.time() - stime))
    print ''

def refiner_basic(candidate_file_list, out_fprefix, threshold):
    stime = time.time()
    print '*************** get images path *****************'
    candidate_images_list = _get_images_path(candidate_file_list)
    print("--- get images path cost %s seconds ---" % (time.time() - stime))
    print ''
    # limit the candidate_images_list size up to 15000
    if len(candidate_images_list) > 18000:
        candidate_images_list = candidate_images_list[0:18000]
        #candidate_images_list = random.sample(candidate_images_list, 14000)

    stime = time.time()
    print '*************** extract candidate images features *****************'
    candidate_images_feature_dict, candidate_images_valid_list = _extract_image_features(candidate_images_list)
    print("--- extract candidate images feature cost %s seconds ---" % (time.time() - stime))
    print ''

    stime = time.time()
    print '*************** compress candidate images features *****************'
    candidate_images_compressed_feature_dict, candidate_eigenvecs_dict, candidate_images_mean_dict = _feature_compression(candidate_images_feature_dict, FeatureNumber)
    print("--- compress candidate images feature cost %s seconds ---" % (time.time() - stime))
    print ''

    stime = time.time()
    print '*************** calculate corrcoef *****************'
    corr_coefs = _calc_corr_coef_basic(candidate_images_compressed_feature_dict)
    print("--- calculate corrcoef cost %s seconds ---" % (time.time() - stime))
    print ''
    print 'corr_coefs', corr_coefs.shape

    stime = time.time()
    print '*************** get similar dict *****************'
    similar_dict = _get_similar_basic(corr_coefs, threshold)
    print("--- get similar dict cost %s seconds ---" % (time.time() - stime))
    print ''

    stime = time.time()
    print '*************** save refined images infos *****************'
    _save_refined_infos_basic(candidate_images_valid_list, similar_dict, out_fprefix)
    print("--- save refined images infos cost %s seconds ---" % (time.time() - stime))
    print ''

def _get_train_val_file_list(infos):
    synsets_path = '/home/lpzhang/Desktop/ImageNetData/synsets_200.txt'
    train_dprefix = '/home/lpzhang/Desktop/ImageNetData/ImageNet/ILSVRC2014/ILSVRC2013_DET_train'
    val_fprefix = '/home/lpzhang/Desktop/ImageNetData/ilsvrc1314_val/ilsvrc1314_val_cls_'
    synsets = dict()
    train_val_file_list = list()
    # synsets
    synsets_infos = _get_infos_from_textfile(synsets_path)
    for eachinfo in synsets_infos:
        eachinfo = eachinfo.split()
        synsets[eachinfo[1]] = eachinfo[0]

    for i in range(0, len(infos)):
        # train data
        wnid = infos[i]
        train_dir = os.path.normpath(train_dprefix) + '/' + wnid
        train_val_file_list.extend(_get_files_abspath_from_directory(train_dir))
        print("wnid %s image size %d" % (wnid, len(train_val_file_list)))

        # val data
        if synsets.has_key(wnid):
            clsid = synsets[wnid]
            fval_path = val_fprefix + clsid + '.txt'
            train_val_file_list.extend(_get_infos_from_textfile(fval_path))
            print("clsid %s wnid %s image size %d" % (clsid, wnid, len(train_val_file_list)))

    return train_val_file_list

def _get_candidate_file_list(infos):
    file_path_list = list()
    file_id_list = list()

    for index in range(0, len(infos)):
        print("File %d (%d)" % (index+1, len(infos)))
        fpath = infos[index]
        fdir, fext = os.path.splitext(fpath)
        id_url_list = _get_infos_from_textfile(fpath)
        for id_url in id_url_list:
            id_url = id_url.split()
            if id_url[0] not in file_id_list:
                file_id_list.append(id_url[0])
                file_path_list.append(os.path.normpath(fdir) + '/' + id_url[0] + '.jpg')

    return file_path_list

def refine_from_itself(infos, threshold, dtype):
    ### each infos contain same object candidate files
    candidate_fpath = os.path.normpath(infos[0])
    out_fprefix = candidate_fpath + '_' + dtype

    for candidate_fpath in infos:
        assert os.path.exists(candidate_fpath), 'candidate_fpath not exist'
        assert os.path.isfile(candidate_fpath), 'candidate_fpath is not a file'
        print 'candidate_fpath:', candidate_fpath

    print 'out_fprefix:', out_fprefix

    # get file list
    stime = time.time()
    print '*************** get candidate file list *****************'
    candidate_files = _get_candidate_file_list(infos)
    print("--- get candidate file list cost %s seconds ---" % (time.time() - stime))
    print ''

    # call the refiner_basic
    refiner_basic(candidate_files, out_fprefix, threshold)

def refine_from_det_train_val(infos, threshold, dtype):
    candidate_fpath = os.path.normpath(infos[0])
    out_fprefix = candidate_fpath + '_' + dtype

    assert os.path.exists(candidate_fpath), 'candidate_fpath not exist'
    assert os.path.isfile(candidate_fpath), 'candidate_fpath is not a file'

    print 'candidate_fpath:', candidate_fpath
    print 'out_fprefix:', out_fprefix

    # get file list
    stime = time.time()
    print '*************** get file list *****************'
    candidate_files = _get_infos_from_textfile(candidate_fpath)
    infos = infos[1:len(infos)]
    gt_files = _get_train_val_file_list(infos)
    print("--- get get file list cost %s seconds ---" % (time.time() - stime))
    print ''

    # call the refiner_advance
    refiner_advance(gt_files, candidate_files, out_fprefix, threshold)

def refine_from_det_test(infos, threshold, dtype):
    # each infos contains candidate file path, gt file path or gtdir
    candidate_fpath = os.path.normpath(infos[0])
    out_fprefix = candidate_fpath + '_' + dtype
    gt_fdir = os.path.normpath(infos[1])

    assert os.path.exists(candidate_fpath), 'candidate_fpath not exist'
    assert os.path.isfile(candidate_fpath), 'candidate_fpath is not a file'
    assert os.path.exists(gt_fdir), 'gt_fdir not exist'
    assert os.path.isdir(gt_fdir), 'gt_fdir is not a dir'

    print 'candidate_fpath:', candidate_fpath
    print 'out_fprefix:', out_fprefix

    # get file list
    stime = time.time()
    print '*************** get file list *****************'
    candidate_files = _get_infos_from_textfile(candidate_fpath)
    gt_files = _get_files_abspath_from_directory(gt_fdir)
    print("--- get get file list cost %s seconds ---" % (time.time() - stime))
    print ''

    # call the refiner_advance
    refiner_advance(gt_files, candidate_files, out_fprefix, threshold)

def refine_wrapper(infos, threshold, dtype):
    assert dtype in ['ITSELF', 'TRAIN', 'TEST'], 'dtype undefined'

    if dtype == 'ITSELF':
        print 'refine from itself'
        refine_from_itself(infos, threshold, dtype)
    elif dtype == 'TRAIN':
        print 'refine from train'
        refine_from_det_train_val(infos, threshold, dtype)
    else:
        print 'refine from test'
        refine_from_det_test(infos, threshold, dtype)

def main(arg):
    start_time = time.time()
    if FLAG_python is True:
        # for python run in command-line
        dtype = str(args.dtype)
        fpath = os.path.normpath(args.fpath)
        threshold = float(args.threshold)
        print 'Python'
    else:
        # for jupyter
        dtype = str(args['dtype'])
        fpath = os.path.normpath(args['fpath'])
        threshold = float(args['threshold'])
        print 'Jupyter'

    infos = _get_infos_from_textfile(fpath)
    for eachinfo in infos:
        eachinfo = eachinfo.split()
        refine_wrapper(eachinfo, threshold, dtype)

    print("------------- total cost %s seconds ----------" % (time.time() - start_time))
    print '++++++++++++++++++++++++++ DONE ++++++++++++++++++++++++++++++++++'

if FLAG_python is True:
    if __name__ == "__main__":
        parser = ArgumentParser(description="Refine Images")
        parser.add_argument('-dtype', required=True)
        parser.add_argument('-fpath', required=True)
        parser.add_argument('-threshold', required=True)
        args = parser.parse_args()
        main(args)
else:
    args = {}
    args['dtype'] = 'ITSELF' # TEST, TRAIN
    args['fpath'] = '/home/lpzhang/Desktop/crawler/refine_images/refiner/refine_itself.txt'
    args['threshold'] = 0.5
    main(args)
